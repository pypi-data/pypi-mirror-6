#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <assert.h>

#define THREADS_PER_BLOCK %d
#define MAX_NUM_LABELS %d
#define SAMPLE_DATA_TYPE %s
#define LABEL_DATA_TYPE %s
#define COUNT_DATA_TYPE %s
#define IDX_DATA_TYPE %s
#define DEBUG %d

#include "common_func.cu"

#define WARP_SIZE 32
#define WARP_MASK 0x1f
texture<char, 1> tex_mark;
__device__ __constant__ uint32_t stride;
__device__ __constant__ uint16_t n_features;
__device__ __constant__ uint16_t max_features;
__device__ __constant__ IDX_DATA_TYPE* sorted_indices_1;
__device__ __constant__ IDX_DATA_TYPE* sorted_indices_2;

__global__ void scan_bfs(
                          LABEL_DATA_TYPE *labels,
                          COUNT_DATA_TYPE *label_total,
                          uint8_t *si_idx,
                          uint32_t *begin_stop_idx
                          ){
  
  IDX_DATA_TYPE *p_sorted_indices;
  IDX_DATA_TYPE reg_start_idx;
  IDX_DATA_TYPE reg_stop_idx;
  __shared__ int shared_count[MAX_NUM_LABELS];
  //__shared__ LABEL_DATA_TYPE shared_labels[THREADS_PER_BLOCK];

  for(uint16_t i = threadIdx.x; i < MAX_NUM_LABELS; i += blockDim.x)
    shared_count[i] = 0;
  
  reg_start_idx = begin_stop_idx[2 * blockIdx.x];
  reg_stop_idx = begin_stop_idx[2 * blockIdx.x + 1];
  
  uint8_t reg_si_idx = si_idx[blockIdx.x];
  if(reg_si_idx == 0)
    p_sorted_indices = sorted_indices_1;
  else 
    p_sorted_indices = sorted_indices_2;
  
  __syncthreads();

  for(IDX_DATA_TYPE i = reg_start_idx; i < reg_stop_idx; i += blockDim.x){
    IDX_DATA_TYPE idx = i + threadIdx.x;

    if(idx < reg_stop_idx)
      atomicAdd(shared_count + labels[p_sorted_indices[idx]], 1);
  }

  __syncthreads();

  for(uint16_t i = threadIdx.x; i < MAX_NUM_LABELS; i += blockDim.x)
    label_total[blockIdx.x * MAX_NUM_LABELS + i] = shared_count[i];
}

__global__ void compute_2d(
                        SAMPLE_DATA_TYPE *samples, 
                        LABEL_DATA_TYPE *labels,
                        uint32_t *begin_stop_idx,
                        uint8_t *si_idx,
                        COUNT_DATA_TYPE *label_total,
                        uint16_t *subset_indices, 
                        float *imp_min, 
                        COUNT_DATA_TYPE *split,
                        uint16_t *min_feature_idx
                        ){

  IDX_DATA_TYPE* p_sorted_indices;
  IDX_DATA_TYPE reg_start_idx;
  IDX_DATA_TYPE reg_stop_idx;
  int32_t reg_feature_min_idx = 0;

  __shared__ IDX_DATA_TYPE shared_count_total[MAX_NUM_LABELS];
  __shared__ IDX_DATA_TYPE shared_label_count[MAX_NUM_LABELS];
  __shared__ LABEL_DATA_TYPE shared_labels[THREADS_PER_BLOCK];
  __shared__ SAMPLE_DATA_TYPE shared_samples[THREADS_PER_BLOCK];
    
  reg_start_idx = begin_stop_idx[2 * blockIdx.x];
  reg_stop_idx = begin_stop_idx[2 * blockIdx.x + 1];
  
  //uint16_t step = blockDim.x - 1;
  float reg_min_left = 2.0;
  float reg_min_right = 2.0;
  IDX_DATA_TYPE reg_min_split = reg_stop_idx;
  float n_samples = reg_stop_idx - reg_start_idx;
  
  int32_t left_sqr_sum = 0;
  int32_t right_sqr_sum_origin = 0;
  int32_t right_sqr_sum;

  for(int32_t i = threadIdx.x; i < MAX_NUM_LABELS; i += blockDim.x)
    shared_count_total[i] = label_total[blockIdx.x * MAX_NUM_LABELS + i];
  
  __syncthreads();

  if(threadIdx.x == 0){
    for(int32_t i = 0; i < MAX_NUM_LABELS; ++i){
      int32_t temp = shared_count_total[i];
      right_sqr_sum_origin += temp * temp;  
    }
  }

  uint8_t reg_si_idx = si_idx[blockIdx.x];
  if(reg_si_idx == 0)
    p_sorted_indices = sorted_indices_1;
  else
    p_sorted_indices = sorted_indices_2;
  
  int32_t feature_idx;
  int32_t offset;
  
  //Number of features thie block needs to check
  int32_t n_tasks = max_features / gridDim.y;

  if(blockIdx.y < max_features %% gridDim.y)
    n_tasks++;
  
  //number of features this block has already checked
  int32_t n_tasks_finished = 0;

  for(int32_t f = blockIdx.y; f < n_features; f += gridDim.y){
    feature_idx = subset_indices[f];
    offset = feature_idx * stride;

    if(n_tasks_finished == n_tasks)
      break;
  
    if(samples[offset + p_sorted_indices[offset + reg_start_idx]] == 
        samples[offset + p_sorted_indices[offset + reg_stop_idx - 1]])
      continue;
    
    right_sqr_sum = right_sqr_sum_origin;
    left_sqr_sum = 0;
  
    //Reset shared_label_count array.
    for(int32_t t = threadIdx.x; t < MAX_NUM_LABELS; t += blockDim.x)
      shared_label_count[t] = 0;
    
    __syncthreads();

    for(IDX_DATA_TYPE i = reg_start_idx; i < reg_stop_idx - 1; i += (blockDim.x - 1)){
      IDX_DATA_TYPE idx = i + threadIdx.x;

      if(idx < reg_stop_idx){
        shared_labels[threadIdx.x] = labels[p_sorted_indices[offset + idx]];
        shared_samples[threadIdx.x] = samples[offset + p_sorted_indices[offset + idx]];
      }

      __syncthreads();

      if(threadIdx.x == 0){
        IDX_DATA_TYPE stop_pos = (i + (blockDim.x - 1) < reg_stop_idx - 1)? (blockDim.x - 1) : reg_stop_idx - 1 - i;
        
        for(IDX_DATA_TYPE t = 0; t < stop_pos; ++t){
          LABEL_DATA_TYPE l_val = shared_labels[t];
          
          int32_t left_cnt = shared_label_count[l_val];
          int32_t right_cnt = shared_count_total[l_val] - left_cnt;
          left_sqr_sum = left_sqr_sum + 2 * left_cnt + 1;
          right_sqr_sum = right_sqr_sum - 2 * right_cnt + 1; 
          
          shared_label_count[l_val]++; 
          
          if(shared_samples[t] + DIFF_THRESHOLD >= shared_samples[t + 1])
            continue;
          
          float n_left =  i + t - reg_start_idx + 1;
          float imp_left = (1.0 - (float)left_sqr_sum / (n_left * n_left)) * (n_left / n_samples);

          float n_right = reg_stop_idx - reg_start_idx - n_left; 
          float imp_right = (1.0 - (float)right_sqr_sum / (n_right * n_right)) * (n_right / n_samples); 

          if(imp_left + imp_right < reg_min_left + reg_min_right){
            reg_min_left = imp_left;
            reg_min_right = imp_right;
            reg_min_split = i + t;
            reg_feature_min_idx = feature_idx;
          }
        }  
      }
      __syncthreads();
    }

    n_tasks_finished++;
  }

  if(threadIdx.x == 0){
    offset = gridDim.y * blockIdx.x + blockIdx.y; 
    imp_min[offset * 2] = reg_min_left;
    imp_min[offset * 2 + 1] = reg_min_right;
    split[offset] = reg_min_split;
    min_feature_idx[offset] = reg_feature_min_idx;
  }
}


__global__ void reduce(float *imp_min_2d, 
                        IDX_DATA_TYPE *split_2d,
                        uint16_t *min_feature_idx_2d,
                        float *imp_min,
                        IDX_DATA_TYPE *split,
                        uint16_t *min_feature,
                        int nblocks){
  
  uint16_t offset = blockIdx.x * nblocks;
  IDX_DATA_TYPE reg_min_split;
  float reg_min_left = 4.0;
  float reg_min_right = 4.0;
  uint16_t reg_min_fidx = 0;
  
  for(int i = 0; i < nblocks; ++i){
    float left = imp_min_2d[2 * (offset + i)];
    float right = imp_min_2d[2 * (offset + i) + 1];
    if(reg_min_left + reg_min_right > left + right){
      reg_min_left = left;
      reg_min_right = right;
      reg_min_fidx = min_feature_idx_2d[offset + i];
      reg_min_split = split_2d[offset + i];
    }
  }
  
  split[blockIdx.x] = reg_min_split;
  min_feature[blockIdx.x] = reg_min_fidx;
  imp_min[2 * blockIdx.x] = reg_min_left;
  imp_min[2 * blockIdx.x + 1] = reg_min_right;
}


__global__ void fill_table(
                          uint8_t *si_idx,
                          uint16_t *feature_idx,
                          uint32_t  *begin_end_idx,
                          IDX_DATA_TYPE *min_split,
                          uint8_t *mark_table
                          ){
  
  IDX_DATA_TYPE reg_stop_idx = begin_end_idx[2 * blockIdx.x + 1];
  IDX_DATA_TYPE reg_split = min_split[blockIdx.x];

  if(reg_split == reg_stop_idx)
    return;
  
  IDX_DATA_TYPE reg_start_idx = begin_end_idx[2 * blockIdx.x];
  uint16_t reg_fidx = feature_idx[blockIdx.x];
  uint8_t reg_si_idx = si_idx[blockIdx.x];
  IDX_DATA_TYPE* p_sorted_indices = (reg_si_idx == 0)? sorted_indices_1 : sorted_indices_2;
  uint32_t offset = reg_fidx * stride;

  for(int t = threadIdx.x + reg_start_idx; t < reg_stop_idx; t += blockDim.x){
    if(t <= reg_split)
      mark_table[p_sorted_indices[offset + t]] = 1;
    else
      mark_table[p_sorted_indices[offset + t]] = 0; 
  }  
}

__global__ void scan_reshuffle(
                          uint8_t* si_idx,
                          uint32_t* begin_end_idx,
                          IDX_DATA_TYPE* split
                          ){  
  
  __shared__ IDX_DATA_TYPE last_sum;
   
#if defined(__CUDA_ARCH__) && __CUDA_ARCH__ >= 300
  uint16_t lane_id = threadIdx.x & WARP_MASK;
  uint16_t warp_id = threadIdx.x / WARP_SIZE;
  __shared__ IDX_DATA_TYPE shared_pos_table[THREADS_PER_BLOCK / WARP_SIZE];
#else
  __shared__ IDX_DATA_TYPE shared_pos_table[THREADS_PER_BLOCK];
#endif 
  
  IDX_DATA_TYPE reg_start_idx = begin_end_idx[2 * blockIdx.x];
  IDX_DATA_TYPE reg_stop_idx = begin_end_idx[2 * blockIdx.x + 1];
  IDX_DATA_TYPE reg_split_idx = split[blockIdx.x];
  IDX_DATA_TYPE n;
  
  
  if(reg_split_idx == reg_stop_idx)
    return;
  

  IDX_DATA_TYPE *p_sorted_indices_in;
  IDX_DATA_TYPE *p_sorted_indices_out;

  if(si_idx[blockIdx.x] == 0){
    p_sorted_indices_in = sorted_indices_1;
    p_sorted_indices_out = sorted_indices_2;
  }else{
    p_sorted_indices_in = sorted_indices_2;
    p_sorted_indices_out = sorted_indices_1;
  }
  
  for(uint16_t shuffle_feature_idx = blockIdx.y; shuffle_feature_idx < n_features; shuffle_feature_idx += gridDim.y){
    uint32_t offset = shuffle_feature_idx * stride;

    if(threadIdx.x == 0)
      last_sum = 0;

    for(IDX_DATA_TYPE i = reg_start_idx; i < reg_stop_idx; i += blockDim.x){
      uint8_t side = 0;
      IDX_DATA_TYPE idx = i + threadIdx.x;
      IDX_DATA_TYPE reg_pos;
      IDX_DATA_TYPE si_idx; 
      
      if(idx < reg_stop_idx){
        si_idx = p_sorted_indices_in[offset + idx];
        side = tex1Dfetch(tex_mark, si_idx);
      }

      reg_pos = side;

#if defined(__CUDA_ARCH__) && __CUDA_ARCH__ >= 300

      for(uint16_t s = 1; s < WARP_SIZE; s *= 2){
        n = __shfl_up((int)reg_pos, s);
        if(lane_id >= s)
          reg_pos += n;
      }

      if(lane_id == WARP_SIZE - 1)
        shared_pos_table[warp_id] = reg_pos;
     
      __syncthreads();
     
      if(threadIdx.x == 0)
        for(uint16_t l = 1; l < blockDim.x / WARP_SIZE - 1; ++l)
          shared_pos_table[l] += shared_pos_table[l-1];

      __syncthreads();
      
      if(warp_id > 0)
        reg_pos += shared_pos_table[warp_id - 1];
      
      reg_pos += last_sum; 

#else
      shared_pos_table[threadIdx.x] = side;
      
      __syncthreads();

      for(uint16_t s = 1; s < blockDim.x; s *= 2){
        if(threadIdx.x >= s)
          n = shared_pos_table[threadIdx.x - s];
        else
          n = 0;
        __syncthreads();
        shared_pos_table[threadIdx.x] += n;
        __syncthreads();
      }
      
      reg_pos = shared_pos_table[threadIdx.x] + last_sum;
#endif

      if(idx < reg_stop_idx){
        IDX_DATA_TYPE out_pos = (side == 1)? reg_start_idx + reg_pos - 1 : reg_split_idx + 1 + idx - reg_start_idx - reg_pos;
        p_sorted_indices_out[offset + out_pos] = si_idx;   
      }

      __syncthreads();

      if(threadIdx.x == blockDim.x - 1)
        last_sum = reg_pos;
    }
     
    __syncthreads();
  }
}

__global__ void get_thresholds
                            (
                            uint8_t *si_idx,
                            SAMPLE_DATA_TYPE *samples,
                            float *threshold_values,
                            uint16_t *min_feature_indices,
                            IDX_DATA_TYPE *min_split_idx
                            ){
    
  IDX_DATA_TYPE *p_sorted_indices;
  uint8_t idx = si_idx[blockIdx.x];
  uint16_t row = min_feature_indices[blockIdx.x];
  IDX_DATA_TYPE col = min_split_idx[blockIdx.x];
  uint32_t offset = row * stride;

  if(idx == 0)
    p_sorted_indices = sorted_indices_1;
  else
    p_sorted_indices = sorted_indices_2;
   
  threshold_values[blockIdx.x] = ((float)samples[offset + p_sorted_indices[offset + col]] + 
                                    samples[offset + p_sorted_indices[offset + col + 1]]) / 2;
}
