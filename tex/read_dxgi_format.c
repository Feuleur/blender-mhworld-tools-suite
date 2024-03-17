#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <stdint.h>


#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT  
#include <omp.h>
#endif

float sRGB_to_linear(float v) {
    return v <= 0.04045 ? v * 12.92 : powf((v + 0.055) / 1.055, 2.4);
}

float linear_to_sRGB(float v) {
    return v <= 0.0031308 ? v * 12.92 : powf(v, 1.0/2.4) * 1.055 - 0.055;
}

EXPORT int read_bc1(void* v_src, void* v_dst, uint32_t width, uint32_t height) {
    uint8_t* src = (uint8_t*) v_src;
    uint8_t* dst = (uint8_t*) v_dst;
    uint32_t texel_size = 2+2+4;
#ifndef _WIN32
    #pragma omp parallel for schedule(static)
#endif
    for (int texel_y=0 ; texel_y<height/4 ; ++texel_y){
        for (int texel_x=0 ; texel_x<width/4 ; ++texel_x){
            // There's some fuckery happening when the image is wide
            uint32_t true_texel_x = texel_x;
//             if (width > height) {
//                 true_texel_x = (((((width/4)/(height/4))-1) - (texel_x/(height/4)))*(height/4)) + (texel_x%(height/4));
//             }
            
            uint32_t texel_offset = texel_size * ((texel_y*width/4) + texel_x);
            uint8_t Rs[4];
            uint8_t Gs[4];
            uint8_t Bs[4];
            uint8_t As[4];
            
            uint16_t color_0 = *((uint16_t*)&src[texel_offset + 0]);
            uint16_t color_1 = *((uint16_t*)&src[texel_offset + 2]);

            Rs[0] = (uint8_t)((((color_0 >> 11) & 31)/31.0)*255);
            Gs[0] = (uint8_t)((((color_0 >> 5) & 63)/63.0)*255);
            Bs[0] = (uint8_t)((((color_0 >> 0) & 31)/31.0)*255);
            As[0] = 255;

            Rs[1] = (uint8_t)((((color_1 >> 11) & 31)/31.0)*255);
            Gs[1] = (uint8_t)((((color_1 >> 5) & 63)/63.0)*255);
            Bs[1] = (uint8_t)((((color_1 >> 0) & 31)/31.0)*255);
            As[1] = 255;

            if(color_0 > color_1) {
                Rs[2] = (uint8_t)(((2.0/3.0)*Rs[0]) + (1.0/3.0)*Rs[1]);
                Gs[2] = (uint8_t)(((2.0/3.0)*Gs[0]) + (1.0/3.0)*Gs[1]);
                Bs[2] = (uint8_t)(((2.0/3.0)*Bs[0]) + (1.0/3.0)*Bs[1]);
                As[2] = 255;

                Rs[3] = (uint8_t)(((1.0/3.0)*Rs[0]) + (2.0/3.0)*Rs[1]);
                Gs[3] = (uint8_t)(((1.0/3.0)*Gs[0]) + (2.0/3.0)*Gs[1]);
                Bs[3] = (uint8_t)(((1.0/3.0)*Bs[0]) + (2.0/3.0)*Bs[1]);
                As[3] = 255;
            } else {
                Rs[2] = (uint8_t)(((1.0/2.0)*Rs[0]) + (1.0/2.0)*Rs[1]);
                Gs[2] = (uint8_t)(((1.0/2.0)*Gs[0]) + (1.0/2.0)*Gs[1]);
                Bs[2] = (uint8_t)(((1.0/2.0)*Bs[0]) + (1.0/2.0)*Bs[1]);
                As[2] = 255;

                Rs[3] = 0;
                Gs[3] = 0;
                Bs[3] = 0;
                As[3] = 0;
            }
            
            uint32_t AP = *((uint32_t*)&src[texel_offset + 4]);
            for (int pixel_y=0 ; pixel_y<4 ; ++pixel_y){
                for (int pixel_x=0 ; pixel_x<4 ; ++pixel_x){
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 0] = Rs[(AP >> (pixel_y*4 + pixel_x)*2) & 3];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 1] = Gs[(AP >> (pixel_y*4 + pixel_x)*2) & 3];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 2] = Bs[(AP >> (pixel_y*4 + pixel_x)*2) & 3];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = As[(AP >> (pixel_y*4 + pixel_x)*2) & 3];
                }
            }
        }
    }
    return 0;
}

EXPORT int read_bc3(void* v_src, void* v_dst, uint32_t width, uint32_t height) {
    uint8_t* src = (uint8_t*) v_src;
    uint8_t* dst = (uint8_t*) v_dst;
    uint32_t texel_size = 1+1+3+3+2+2+4;
#ifndef _WIN32
    #pragma omp parallel for schedule(static)
#endif
    for (int texel_y=0 ; texel_y<height/4 ; ++texel_y){
        for (int texel_x=0 ; texel_x<width/4 ; ++texel_x){
            // There's some fuckery happening when the image is wide
            uint32_t true_texel_x = texel_x;
//             if (width > height) {
//                 true_texel_x = (((((width/4)/(height/4))-1) - (texel_x/(height/4)))*(height/4)) + (texel_x%(height/4));
//             }

            uint32_t texel_offset = texel_size * ((texel_y*width/4) + texel_x);

            uint8_t Cs[8];
            Cs[0] = *((uint8_t*)&src[texel_offset + 0]);
            Cs[1] = *((uint8_t*)&src[texel_offset + 1]);
            if (Cs[0] > Cs[1]) {
                Cs[2] = ((6.0/7.0)*Cs[0]) + ((1.0/7.0)*Cs[1]);
                Cs[3] = ((5.0/7.0)*Cs[0]) + ((2.0/7.0)*Cs[1]);
                Cs[4] = ((4.0/7.0)*Cs[0]) + ((3.0/7.0)*Cs[1]);
                Cs[5] = ((3.0/7.0)*Cs[0]) + ((4.0/7.0)*Cs[1]);
                Cs[6] = ((2.0/7.0)*Cs[0]) + ((5.0/7.0)*Cs[1]);
                Cs[7] = ((1.0/7.0)*Cs[0]) + ((6.0/7.0)*Cs[1]);
            } else {
                Cs[2] = ((4.0/5.0)*Cs[0]) + ((1.0/5.0)*Cs[1]);
                Cs[3] = ((3.0/5.0)*Cs[0]) + ((2.0/5.0)*Cs[1]);
                Cs[4] = ((2.0/5.0)*Cs[0]) + ((3.0/5.0)*Cs[1]);
                Cs[5] = ((1.0/5.0)*Cs[0]) + ((4.0/5.0)*Cs[1]);
                Cs[6] = 0;
                Cs[7] = 255;
            }
            uint64_t AP_alpha = *((uint64_t*)&src[texel_offset + 2]);
            AP_alpha = AP_alpha >> 0 & 281474976710655;

            uint8_t Rs[4];
            uint8_t Gs[4];
            uint8_t Bs[4];
            short color_0 = *((short*)&src[texel_offset + 8]);
            Rs[0] = (uint8_t)((((color_0 >> 11) & 31)/31.0)*255);
            Gs[0] = (uint8_t)((((color_0 >> 5) & 63)/63.0)*255);
            Bs[0] = (uint8_t)((((color_0 >> 0) & 31)/31.0)*255);
            short color_1 = *((short*)&src[texel_offset + 10]);
            Rs[1] = (uint8_t)((((color_1 >> 11) & 31)/31.0)*255);
            Gs[1] = (uint8_t)((((color_1 >> 5) & 63)/63.0)*255);
            Bs[1] = (uint8_t)((((color_1 >> 0) & 31)/31.0)*255);

            Rs[2] = (uint8_t)(((2.0/3.0)*Rs[0]) + (1.0/3.0)*Rs[1]);
            Gs[2] = (uint8_t)(((2.0/3.0)*Gs[0]) + (1.0/3.0)*Gs[1]);
            Bs[2] = (uint8_t)(((2.0/3.0)*Bs[0]) + (1.0/3.0)*Bs[1]);

            Rs[3] = (uint8_t)(((1.0/3.0)*Rs[0]) + (2.0/3.0)*Rs[1]);
            Gs[3] = (uint8_t)(((1.0/3.0)*Gs[0]) + (2.0/3.0)*Gs[1]);
            Bs[3] = (uint8_t)(((1.0/3.0)*Bs[0]) + (2.0/3.0)*Bs[1]);

            uint32_t AP_color = *((uint32_t*)&src[texel_offset + 12]);
            for (int pixel_y=0 ; pixel_y<4 ; ++pixel_y){
                for (int pixel_x=0 ; pixel_x<4 ; ++pixel_x){
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 0] = Rs[(AP_color >> (pixel_y*4 + pixel_x)*2) & 3];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 1] = Gs[(AP_color >> (pixel_y*4 + pixel_x)*2) & 3];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 2] = Bs[(AP_color >> (pixel_y*4 + pixel_x)*2) & 3];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = Cs[(AP_alpha >> (pixel_y*4 + pixel_x)*3) & 7];
//                     dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = 255;
                }
            }
        }
    }
    return 0;
}

EXPORT int read_bc4(void* v_src, void* v_dst, uint32_t width, uint32_t height) {
    uint8_t* src = (uint8_t*) v_src;
    uint8_t* dst = (uint8_t*) v_dst;
    uint32_t texel_size = 1+1+6;
#ifndef _WIN32
    #pragma omp parallel for schedule(static)
#endif
    for (int texel_y=0 ; texel_y<height/4 ; ++texel_y){
        for (int texel_x=0 ; texel_x<width/4 ; ++texel_x){
            // There's some fuckery happening when the image is wide
            uint32_t true_texel_x = texel_x;
//             if (width > height) {
//                 true_texel_x = (((((width/4)/(height/4))-1) - (texel_x/(height/4)))*(height/4)) + (texel_x%(height/4));
//             }
            uint32_t texel_offset = texel_size * ((texel_y*width/4) + texel_x);
            
            uint8_t Cs[8];
            Cs[0] = *((uint8_t*)&src[texel_offset + 0]);
            Cs[1] = *((uint8_t*)&src[texel_offset + 1]);
            
            if (Cs[0] > Cs[1]) {
                Cs[2] = ((6*Cs[0] + 1*Cs[1]) / 7.0);
                Cs[3] = ((5*Cs[0] + 2*Cs[1]) / 7.0);
                Cs[4] = ((4*Cs[0] + 3*Cs[1]) / 7.0);
                Cs[5] = ((3*Cs[0] + 4*Cs[1]) / 7.0);
                Cs[6] = ((2*Cs[0] + 5*Cs[1]) / 7.0);
                Cs[7] = ((1*Cs[0] + 6*Cs[1]) / 7.0);
            } else {
                Cs[2] = ((4*Cs[0] + 1*Cs[1]) / 5.0);
                Cs[3] = ((3*Cs[0] + 2*Cs[1]) / 5.0);
                Cs[4] = ((2*Cs[0] + 3*Cs[1]) / 5.0);
                Cs[5] = ((1*Cs[0] + 4*Cs[1]) / 5.0);
                Cs[6] = 0;
                Cs[7] = 255;
            }
            
            uint64_t AP = *((uint64_t*)&src[texel_offset + 0]);
            AP = AP >> 16 & 281474976710655;
            
            for (int pixel_y=0 ; pixel_y<4 ; ++pixel_y){
                for (int pixel_x=0 ; pixel_x<4 ; ++pixel_x){
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 0] = Cs[(AP >> (pixel_y*4 + pixel_x)*3) & 7];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 1] = Cs[(AP >> (pixel_y*4 + pixel_x)*3) & 7];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 2] = Cs[(AP >> (pixel_y*4 + pixel_x)*3) & 7];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = 255;
                }
            }
        }
    }
    
    return 0;
}

EXPORT int read_bc5(void* v_src, void* v_dst, uint32_t width, uint32_t height) {
    uint8_t* src = (uint8_t*) v_src;
    uint8_t* dst = (uint8_t*) v_dst;
    uint32_t texel_size = 1+1+6+1+1+6;
#ifndef _WIN32
    #pragma omp parallel for schedule(static)
#endif
    for (int texel_y=0 ; texel_y<height/4 ; ++texel_y){
        for (int texel_x=0 ; texel_x<width/4 ; ++texel_x){
            // There's some fuckery happening when the image is wide
            uint32_t true_texel_x = texel_x;
//             if (width > height) {
//                 true_texel_x = (((((width/4)/(height/4))-1) - (texel_x/(height/4)))*(height/4)) + (texel_x%(height/4));
//             }
            uint32_t texel_offset = texel_size * ((texel_y*width/4) + texel_x);
            
            uint8_t Rs[8];
            Rs[0] = *((uint8_t*)&src[texel_offset + 0]);
            Rs[1] = *((uint8_t*)&src[texel_offset + 1]);
            
            if (Rs[0] > Rs[1]) {
                Rs[2] = ((6*Rs[0] + 1*Rs[1]) / 7.0);
                Rs[3] = ((5*Rs[0] + 2*Rs[1]) / 7.0);
                Rs[4] = ((4*Rs[0] + 3*Rs[1]) / 7.0);
                Rs[5] = ((3*Rs[0] + 4*Rs[1]) / 7.0);
                Rs[6] = ((2*Rs[0] + 5*Rs[1]) / 7.0);
                Rs[7] = ((1*Rs[0] + 6*Rs[1]) / 7.0);
            } else {
                Rs[2] = ((4*Rs[0] + 1*Rs[1]) / 5.0);
                Rs[3] = ((3*Rs[0] + 2*Rs[1]) / 5.0);
                Rs[4] = ((2*Rs[0] + 3*Rs[1]) / 5.0);
                Rs[5] = ((1*Rs[0] + 4*Rs[1]) / 5.0);
                Rs[6] = 0;
                Rs[7] = 255;
            }
            uint64_t RAP = *((uint64_t*)&src[texel_offset + 0]);
            RAP = RAP >> 16 & 281474976710655;
            
            uint8_t Gs[8];
            Gs[0] = *((uint8_t*)&src[texel_offset + 8]);
            Gs[1] = *((uint8_t*)&src[texel_offset + 9]);
            
            if (Gs[0] > Gs[1]) {
                Gs[2] = ((6*Gs[0] + 1*Gs[1]) / 7.0);
                Gs[3] = ((5*Gs[0] + 2*Gs[1]) / 7.0);
                Gs[4] = ((4*Gs[0] + 3*Gs[1]) / 7.0);
                Gs[5] = ((3*Gs[0] + 4*Gs[1]) / 7.0);
                Gs[6] = ((2*Gs[0] + 5*Gs[1]) / 7.0);
                Gs[7] = ((1*Gs[0] + 6*Gs[1]) / 7.0);
            } else {
                Gs[2] = ((4*Gs[0] + 1*Gs[1]) / 5.0);
                Gs[3] = ((3*Gs[0] + 2*Gs[1]) / 5.0);
                Gs[4] = ((2*Gs[0] + 3*Gs[1]) / 5.0);
                Gs[5] = ((1*Gs[0] + 4*Gs[1]) / 5.0);
                Gs[6] = 0;
                Gs[7] = 255;
            }
            uint64_t GAP = *((uint64_t*)&src[texel_offset + 8]);
            GAP = GAP >> 16 & 281474976710655;
            for (int pixel_y=0 ; pixel_y<4 ; ++pixel_y){
                for (int pixel_x=0 ; pixel_x<4 ; ++pixel_x){
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 0] = Rs[(RAP >> (pixel_y*4 + pixel_x)*3) & 7];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 1] = Gs[(GAP >> (pixel_y*4 + pixel_x)*3) & 7];
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 2] = 0;
                    dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = 255;
                }
            }
        }
    }
    
    return 0;
}

EXPORT int read_bc7(void* v_src, void* v_dst, uint32_t width, uint32_t height) {
    uint8_t* src = (uint8_t*) v_src;
    uint8_t* dst = (uint8_t*) v_dst;
    uint32_t texel_size = 16;
    
    uint8_t default_partition[16] = {
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0   
    };
    
    uint8_t partition_2_list[64][16] = {
        {0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1},
        {0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1},
        {0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1},
        {0,0,0,1,0,0,1,1,0,0,1,1,0,1,1,1},
        {0,0,0,0,0,0,0,1,0,0,0,1,0,0,1,1},
        {0,0,1,1,0,1,1,1,0,1,1,1,1,1,1,1},
        {0,0,0,1,0,0,1,1,0,1,1,1,1,1,1,1},
        {0,0,0,0,0,0,0,1,0,0,1,1,0,1,1,1},
        {0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1},
        {0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1},
        {0,0,0,0,0,0,0,1,0,1,1,1,1,1,1,1},
        {0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1},
        {0,0,0,1,0,1,1,1,1,1,1,1,1,1,1,1},
        {0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1},
        {0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1},
        {0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1},
        {0,0,0,0,1,0,0,0,1,1,1,0,1,1,1,1},
        {0,1,1,1,0,0,0,1,0,0,0,0,0,0,0,0},
        {0,0,0,0,0,0,0,0,1,0,0,0,1,1,1,0},
        {0,1,1,1,0,0,1,1,0,0,0,1,0,0,0,0},
        {0,0,1,1,0,0,0,1,0,0,0,0,0,0,0,0},
        {0,0,0,0,1,0,0,0,1,1,0,0,1,1,1,0},
        {0,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0},
        {0,1,1,1,0,0,1,1,0,0,1,1,0,0,0,1},
        {0,0,1,1,0,0,0,1,0,0,0,1,0,0,0,0},
        {0,0,0,0,1,0,0,0,1,0,0,0,1,1,0,0},
        {0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0},
        {0,0,1,1,0,1,1,0,0,1,1,0,1,1,0,0},
        {0,0,0,1,0,1,1,1,1,1,1,0,1,0,0,0},
        {0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0},
        {0,1,1,1,0,0,0,1,1,0,0,0,1,1,1,0},
        {0,0,1,1,1,0,0,1,1,0,0,1,1,1,0,0},
        {0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1},
        {0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,1},
        {0,1,0,1,1,0,1,0,0,1,0,1,1,0,1,0},
        {0,0,1,1,0,0,1,1,1,1,0,0,1,1,0,0},
        {0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0},
        {0,1,0,1,0,1,0,1,1,0,1,0,1,0,1,0},
        {0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1},
        {0,1,0,1,1,0,1,0,1,0,1,0,0,1,0,1},
        {0,1,1,1,0,0,1,1,1,1,0,0,1,1,1,0},
        {0,0,0,1,0,0,1,1,1,1,0,0,1,0,0,0},
        {0,0,1,1,0,0,1,0,0,1,0,0,1,1,0,0},
        {0,0,1,1,1,0,1,1,1,1,0,1,1,1,0,0},
        {0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0},
        {0,0,1,1,1,1,0,0,1,1,0,0,0,0,1,1},
        {0,1,1,0,0,1,1,0,1,0,0,1,1,0,0,1},
        {0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0},
        {0,1,0,0,1,1,1,0,0,1,0,0,0,0,0,0},
        {0,0,1,0,0,1,1,1,0,0,1,0,0,0,0,0},
        {0,0,0,0,0,0,1,0,0,1,1,1,0,0,1,0},
        {0,0,0,0,0,1,0,0,1,1,1,0,0,1,0,0},
        {0,1,1,0,1,1,0,0,1,0,0,1,0,0,1,1},
        {0,0,1,1,0,1,1,0,1,1,0,0,1,0,0,1},
        {0,1,1,0,0,0,1,1,1,0,0,1,1,1,0,0},
        {0,0,1,1,1,0,0,1,1,1,0,0,0,1,1,0},
        {0,1,1,0,1,1,0,0,1,1,0,0,1,0,0,1},
        {0,1,1,0,0,0,1,1,0,0,1,1,1,0,0,1},
        {0,1,1,1,1,1,1,0,1,0,0,0,0,0,0,1},
        {0,0,0,1,1,0,0,0,1,1,1,0,0,1,1,1},
        {0,0,0,0,1,1,1,1,0,0,1,1,0,0,1,1},
        {0,0,1,1,0,0,1,1,1,1,1,1,0,0,0,0},
        {0,0,1,0,0,0,1,0,1,1,1,0,1,1,1,0},
        {0,1,0,0,0,1,0,0,0,1,1,1,0,1,1,1}
    };
    
    uint8_t partition_3_list[64][16] = {
        {0,0,1,1,0,0,1,1,0,2,2,1,2,2,2,2},
        {0,0,0,1,0,0,1,1,2,2,1,1,2,2,2,1},
        {0,0,0,0,2,0,0,1,2,2,1,1,2,2,1,1},
        {0,2,2,2,0,0,2,2,0,0,1,1,0,1,1,1},
        {0,0,0,0,0,0,0,0,1,1,2,2,1,1,2,2},
        {0,0,1,1,0,0,1,1,0,0,2,2,0,0,2,2},
        {0,0,2,2,0,0,2,2,1,1,1,1,1,1,1,1},
        {0,0,1,1,0,0,1,1,2,2,1,1,2,2,1,1},
        {0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2},
        {0,0,0,0,1,1,1,1,1,1,1,1,2,2,2,2},
        {0,0,0,0,1,1,1,1,2,2,2,2,2,2,2,2},
        {0,0,1,2,0,0,1,2,0,0,1,2,0,0,1,2},
        {0,1,1,2,0,1,1,2,0,1,1,2,0,1,1,2},
        {0,1,2,2,0,1,2,2,0,1,2,2,0,1,2,2},
        {0,0,1,1,0,1,1,2,1,1,2,2,1,2,2,2},
        {0,0,1,1,2,0,0,1,2,2,0,0,2,2,2,0},
        {0,0,0,1,0,0,1,1,0,1,1,2,1,1,2,2},
        {0,1,1,1,0,0,1,1,2,0,0,1,2,2,0,0},
        {0,0,0,0,1,1,2,2,1,1,2,2,1,1,2,2},
        {0,0,2,2,0,0,2,2,0,0,2,2,1,1,1,1},
        {0,1,1,1,0,1,1,1,0,2,2,2,0,2,2,2},
        {0,0,0,1,0,0,0,1,2,2,2,1,2,2,2,1},
        {0,0,0,0,0,0,1,1,0,1,2,2,0,1,2,2},
        {0,0,0,0,1,1,0,0,2,2,1,0,2,2,1,0},
        {0,1,2,2,0,1,2,2,0,0,1,1,0,0,0,0},
        {0,0,1,2,0,0,1,2,1,1,2,2,2,2,2,2},
        {0,1,1,0,1,2,2,1,1,2,2,1,0,1,1,0},
        {0,0,0,0,0,1,1,0,1,2,2,1,1,2,2,1},
        {0,0,2,2,1,1,0,2,1,1,0,2,0,0,2,2},
        {0,1,1,0,0,1,1,0,2,0,0,2,2,2,2,2},
        {0,0,1,1,0,1,2,2,0,1,2,2,0,0,1,1},
        {0,0,0,0,2,0,0,0,2,2,1,1,2,2,2,1},
        {0,0,0,0,0,0,0,2,1,1,2,2,1,2,2,2},
        {0,2,2,2,0,0,2,2,0,0,1,2,0,0,1,1},
        {0,0,1,1,0,0,1,2,0,0,2,2,0,2,2,2},
        {0,1,2,0,0,1,2,0,0,1,2,0,0,1,2,0},
        {0,0,0,0,1,1,1,1,2,2,2,2,0,0,0,0},
        {0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0},
        {0,1,2,0,2,0,1,2,1,2,0,1,0,1,2,0},
        {0,0,1,1,2,2,0,0,1,1,2,2,0,0,1,1},
        {0,0,1,1,1,1,2,2,2,2,0,0,0,0,1,1},
        {0,1,0,1,0,1,0,1,2,2,2,2,2,2,2,2},
        {0,0,0,0,0,0,0,0,2,1,2,1,2,1,2,1},
        {0,0,2,2,1,1,2,2,0,0,2,2,1,1,2,2},
        {0,0,2,2,0,0,1,1,0,0,2,2,0,0,1,1},
        {0,2,2,0,1,2,2,1,0,2,2,0,1,2,2,1},
        {0,1,0,1,2,2,2,2,2,2,2,2,0,1,0,1},
        {0,0,0,0,2,1,2,1,2,1,2,1,2,1,2,1},
        {0,1,0,1,0,1,0,1,0,1,0,1,2,2,2,2},
        {0,2,2,2,0,1,1,1,0,2,2,2,0,1,1,1},
        {0,0,0,2,1,1,1,2,0,0,0,2,1,1,1,2},
        {0,0,0,0,2,1,1,2,2,1,1,2,2,1,1,2},
        {0,2,2,2,0,1,1,1,0,1,1,1,0,2,2,2},
        {0,0,0,2,1,1,1,2,1,1,1,2,0,0,0,2},
        {0,1,1,0,0,1,1,0,0,1,1,0,2,2,2,2},
        {0,0,0,0,0,0,0,0,2,1,1,2,2,1,1,2},
        {0,1,1,0,0,1,1,0,2,2,2,2,2,2,2,2},
        {0,0,2,2,0,0,1,1,0,0,1,1,0,0,2,2},
        {0,0,2,2,1,1,2,2,1,1,2,2,0,0,2,2},
        {0,0,0,0,0,0,0,0,0,0,0,0,2,1,1,2},
        {0,0,0,2,0,0,0,1,0,0,0,2,0,0,0,1},
        {0,2,2,2,1,2,2,2,0,2,2,2,1,2,2,2},
        {0,1,0,1,2,2,2,2,2,2,2,2,2,2,2,2},
        {0,1,1,1,2,0,1,1,2,2,0,1,2,2,2,0}
    };
    
    uint8_t palette_weights[3][16] = {
        {0, 21, 43, 64}, 
        {0, 9, 18, 27, 37, 46, 55, 64}, 
        {0, 4, 9, 13, 17, 21, 26, 30, 34, 38, 43, 47, 51, 55, 60, 64}
    };

    // Probably not all necessary
    uint8_t anchors[3][3][64] = {
        {
            {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
            {16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16},
            {16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16}
        },
        {
            {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
            {15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,2,8,2,2,8,8,15,2,8,2,2,8,8,2,2,15,15,6,8,2,8,15,15,2,8,2,2,2,15,15,6,6,2,6,8,15,15,2,2,15,15,15,15,15,2,2,15},
            {16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16}
        },
        { 
            {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
            {3,3,15,15,8,3,15,15,8,8,6,6,6,5,3,3,3,3,8,15,3,3,6,10,5,8,8,6,8,5,15,15,8,15,3,5,6,10,8,15,15,3,15,5,15,15,15,15,3,15,5,5,5,8,5,10,5,10,8,13,15,12,3,3},
            {15,8,8,3,15,15,3,8,15,15,15,15,15,15,15,8,15,8,15,3,15,8,15,8,3,15,6,10,15,15,10,8,15,3,15,10,10,8,9,10,6,15,8,15,3,6,6,8,15,3,15,15,15,15,15,15,15,15,15,15,3,15,15,8}
        }
    };

#ifndef _WIN32
    #pragma omp parallel for schedule(static)
#endif
    for (int texel_y=0 ; texel_y<height/4 ; ++texel_y){
        for (int texel_x=0 ; texel_x<width/4 ; ++texel_x){
            // There's some fuckery happening when the image is wide
            uint32_t true_texel_x = texel_x;
//             if (width > height) {
//                 true_texel_x = (((((width/4)/(height/4))-1) - (texel_x/(height/4)))*(height/4)) + (texel_x%(height/4));
//             }
            uint32_t texel_offset = texel_size * ((texel_y*width/4) + texel_x);
            uint8_t mode;
            uint8_t mode_byte = *((uint8_t*)&src[texel_offset + 0]);
            
            uint8_t rot = 0;
            uint8_t* partition = default_partition;
            
            if (mode_byte >> 0 & 1 == 1) {
                mode = 0;
            } else if (mode_byte >> 1 & 1 == 1) {
                mode = 1;
            } else if (mode_byte >> 2 & 1 == 1) {
                mode = 2;
            } else if (mode_byte >> 3 & 1 == 1) {
                mode = 3;
            } else if (mode_byte >> 4 & 1 == 1) {
                mode = 4;
            } else if (mode_byte >> 5 & 1 == 1) {
                mode = 5;
            } else if (mode_byte >> 6 & 1 == 1) {
                mode = 6;
            } else {
                mode = 7;
            }
            
            
            uint8_t V0_raw[3][2];
            uint8_t V1_raw[3][2];
            uint8_t V2_raw[3][2];
            uint8_t S0_raw[3][2];
            uint64_t vector_index_bytes = 0;
            uint64_t scalar_index_bytes = 0;
            uint8_t anchor[3];
            uint8_t n_subsets = 0;
            uint8_t vector_index_precision = 0;
            uint8_t scalar_index_precision = 0;
            uint8_t idx = 0;
            if (mode == 0) {
                uint8_t partition_bytes = *((uint8_t*)&src[texel_offset + 0]);
                partition = partition_3_list[partition_bytes >> 1 & 15];
                anchor[1] = anchors[2][1][partition_bytes >> 1 & 15];
                anchor[2] = anchors[2][2][partition_bytes >> 1 & 15];
                
                uint16_t P_bytes = *((uint16_t*)&src[texel_offset + 9]);
                uint8_t P1 = P_bytes >> 5 & 1;
                uint8_t P2 = P_bytes >> 6 & 1;
                uint8_t P3 = P_bytes >> 7 & 1;
                uint8_t P4 = P_bytes >> 8 & 1;
                uint8_t P5 = P_bytes >> 9 & 1;
                uint8_t P6 = P_bytes >> 10 & 1;
                
                uint32_t v0_bytes = *((uint32_t*)&src[texel_offset + 0]);
                V0_raw[0][0] = ((v0_bytes >> 5 >> 0 & 15) << 1 | P1) << (8-5);
                V0_raw[0][1] = ((v0_bytes >> 5 >> 4 & 15) << 1 | P2) << (8-5);
                V0_raw[1][0] = ((v0_bytes >> 5 >> 8 & 15) << 1 | P3) << (8-5);
                V0_raw[1][1] = ((v0_bytes >> 5 >> 12 & 15) << 1 | P4) << (8-5);
                V0_raw[2][0] = ((v0_bytes >> 5 >> 16 & 15) << 1 | P5) << (8-5);
                V0_raw[2][1] = ((v0_bytes >> 5 >> 20 & 15) << 1 | P6) << (8-5);
                V0_raw[0][0] = V0_raw[0][0] | (V0_raw[0][0] >> 5);
                V0_raw[0][1] = V0_raw[0][1] | (V0_raw[0][1] >> 5);
                V0_raw[1][0] = V0_raw[1][0] | (V0_raw[1][0] >> 5);
                V0_raw[1][1] = V0_raw[1][1] | (V0_raw[1][1] >> 5);
                V0_raw[2][0] = V0_raw[2][0] | (V0_raw[2][0] >> 5);
                V0_raw[2][1] = V0_raw[2][1] | (V0_raw[2][1] >> 5);
                
                uint32_t v1_bytes = *((uint32_t*)&src[texel_offset + 3]);
                V1_raw[0][0] = ((v1_bytes >> 5 >> 0 & 15) << 1 | P1) << (8-5);
                V1_raw[0][1] = ((v1_bytes >> 5 >> 4 & 15) << 1 | P2) << (8-5);
                V1_raw[1][0] = ((v1_bytes >> 5 >> 8 & 15) << 1 | P3) << (8-5);
                V1_raw[1][1] = ((v1_bytes >> 5 >> 12 & 15) << 1 | P4) << (8-5);
                V1_raw[2][0] = ((v1_bytes >> 5 >> 16 & 15) << 1 | P5) << (8-5);
                V1_raw[2][1] = ((v1_bytes >> 5 >> 20 & 15) << 1 | P6) << (8-5);
                V1_raw[0][0] = V1_raw[0][0] | (V1_raw[0][0] >> 5);
                V1_raw[0][1] = V1_raw[0][1] | (V1_raw[0][1] >> 5);
                V1_raw[1][0] = V1_raw[1][0] | (V1_raw[1][0] >> 5);
                V1_raw[1][1] = V1_raw[1][1] | (V1_raw[1][1] >> 5);
                V1_raw[2][0] = V1_raw[2][0] | (V1_raw[2][0] >> 5);
                V1_raw[2][1] = V1_raw[2][1] | (V1_raw[2][1] >> 5);
                
                
                uint32_t v2_bytes = *((uint32_t*)&src[texel_offset + 6]);
                V2_raw[0][0] = ((v2_bytes >> 5 >> 0 & 15) << 1 | P1) << (8-5);
                V2_raw[0][1] = ((v2_bytes >> 5 >> 4 & 15) << 1 | P2) << (8-5);
                V2_raw[1][0] = ((v2_bytes >> 5 >> 8 & 15) << 1 | P3) << (8-5);
                V2_raw[1][1] = ((v2_bytes >> 5 >> 12 & 15) << 1 | P4) << (8-5);
                V2_raw[2][0] = ((v2_bytes >> 5 >> 16 & 15) << 1 | P5) << (8-5);
                V2_raw[2][1] = ((v2_bytes >> 5 >> 20 & 15) << 1 | P6) << (8-5);
                V2_raw[0][0] = V2_raw[0][0] | (V2_raw[0][0] >> 5);
                V2_raw[0][1] = V2_raw[0][1] | (V2_raw[0][1] >> 5);
                V2_raw[1][0] = V2_raw[1][0] | (V2_raw[1][0] >> 5);
                V2_raw[1][1] = V2_raw[1][1] | (V2_raw[1][1] >> 5);
                V2_raw[2][0] = V2_raw[2][0] | (V2_raw[2][0] >> 5);
                V2_raw[2][1] = V2_raw[2][1] | (V2_raw[2][1] >> 5);
                
                S0_raw[0][0] = 255;
                S0_raw[0][1] = 255;
                S0_raw[1][0] = 255;
                S0_raw[1][1] = 255;
                S0_raw[2][0] = 255;
                S0_raw[2][1] = 255;
                
                uint64_t index_bytes = *((uint64_t*)&src[texel_offset + 10]);
                vector_index_bytes = (index_bytes >> 3) & (((uint64_t)(powl(2, 45)+0.5))-1);
                vector_index_precision = 3;
                scalar_index_bytes = vector_index_bytes;
                scalar_index_precision = vector_index_precision;
            } else if (mode == 1) {
                uint8_t partition_bytes = *((uint8_t*)&src[texel_offset + 0]);
                partition = partition_2_list[partition_bytes >> 2 & 63];
                anchor[1] = anchors[1][1][partition_bytes >> 2 & 63];
                anchor[2] = 16;
                
                uint16_t P_bytes = *((uint16_t*)&src[texel_offset + 10]);
                uint8_t P1 = P_bytes >> 0 & 1;
                uint8_t P2 = P_bytes >> 1 & 1;
                
                uint32_t v0_bytes = *((uint32_t*)&src[texel_offset + 1]);
                V0_raw[0][0] = ((v0_bytes >> 0 >> 0 & 63) << 1 | P1) << (8-7);
                V0_raw[0][1] = ((v0_bytes >> 0 >> 6 & 63) << 1 | P1) << (8-7);
                V0_raw[1][0] = ((v0_bytes >> 0 >> 12 & 63) << 1 | P2) << (8-7);
                V0_raw[1][1] = ((v0_bytes >> 0 >> 18 & 63) << 1 | P2) << (8-7);
                V0_raw[0][0] = V0_raw[0][0] | (V0_raw[0][0] >> 7);
                V0_raw[0][1] = V0_raw[0][1] | (V0_raw[0][1] >> 7);
                V0_raw[1][0] = V0_raw[1][0] | (V0_raw[1][0] >> 7);
                V0_raw[1][1] = V0_raw[1][1] | (V0_raw[1][1] >> 7);
                
                uint32_t v1_bytes = *((uint32_t*)&src[texel_offset + 4]);
                V1_raw[0][0] = ((v1_bytes >> 0 >> 0 & 63) << 1 | P1) << (8-7);
                V1_raw[0][1] = ((v1_bytes >> 0 >> 6 & 63) << 1 | P1) << (8-7);
                V1_raw[1][0] = ((v1_bytes >> 0 >> 12 & 63) << 1 | P2) << (8-7);
                V1_raw[1][1] = ((v1_bytes >> 0 >> 18 & 63) << 1 | P2) << (8-7);
                V1_raw[0][0] = V1_raw[0][0] | (V1_raw[0][0] >> 7);
                V1_raw[0][1] = V1_raw[0][1] | (V1_raw[0][1] >> 7);
                V1_raw[1][0] = V1_raw[1][0] | (V1_raw[1][0] >> 7);
                V1_raw[1][1] = V1_raw[1][1] | (V1_raw[1][1] >> 7);
                
                
                uint32_t v2_bytes = *((uint32_t*)&src[texel_offset + 7]);
                V2_raw[0][0] = ((v2_bytes >> 0 >> 0 & 63) << 1 | P1) << (8-7);
                V2_raw[0][1] = ((v2_bytes >> 0 >> 6 & 63) << 1 | P1) << (8-7);
                V2_raw[1][0] = ((v2_bytes >> 0 >> 12 & 63) << 1 | P2) << (8-7);
                V2_raw[1][1] = ((v2_bytes >> 0 >> 18 & 63) << 1 | P2) << (8-7);
                V2_raw[0][0] = V2_raw[0][0] | (V2_raw[0][0] >> 7);
                V2_raw[0][1] = V2_raw[0][1] | (V2_raw[0][1] >> 7);
                V2_raw[1][0] = V2_raw[1][0] | (V2_raw[1][0] >> 7);
                V2_raw[1][1] = V2_raw[1][1] | (V2_raw[1][1] >> 7);
                
                S0_raw[0][0] = 255;
                S0_raw[0][1] = 255;
                S0_raw[1][0] = 255;
                S0_raw[1][1] = 255;

                uint64_t index_bytes = *((uint64_t*)&src[texel_offset + 8]);
                vector_index_bytes = (index_bytes >> 18) & (((uint64_t)(powl(2, 46)+0.5))-1);
                vector_index_precision = 3;
                scalar_index_bytes = vector_index_bytes;
                scalar_index_precision = vector_index_precision;
            } else if (mode == 2) {
                uint16_t partition_bytes = *((uint16_t*)&src[texel_offset + 0]);
                partition = partition_3_list[partition_bytes >> 3 & 63];
                anchor[1] = anchors[2][1][partition_bytes >> 3 & 63];
                anchor[2] = anchors[2][2][partition_bytes >> 3 & 63];
                
                uint64_t v0_bytes = *((uint64_t*)&src[texel_offset + 1]);
                V0_raw[0][0] = ((v0_bytes >> 1 >> 0 & 31)) << 3;
                V0_raw[0][1] = ((v0_bytes >> 1 >> 5 & 31)) << 3;
                V0_raw[1][0] = ((v0_bytes >> 1 >> 10 & 31)) << 3;
                V0_raw[1][1] = ((v0_bytes >> 1 >> 15 & 31)) << 3;
                V0_raw[2][0] = ((v0_bytes >> 1 >> 20 & 31)) << 3;
                V0_raw[2][1] = ((v0_bytes >> 1 >> 25 & 31)) << 3;
                
                uint64_t v1_bytes = *((uint64_t*)&src[texel_offset + 4]);
                V1_raw[0][0] = ((v1_bytes >> 7 >> 0 & 31)) << 3;
                V1_raw[0][1] = ((v1_bytes >> 7 >> 5 & 31)) << 3;
                V1_raw[1][0] = ((v1_bytes >> 7 >> 10 & 31)) << 3;
                V1_raw[1][1] = ((v1_bytes >> 7 >> 15 & 31)) << 3;
                V1_raw[2][0] = ((v1_bytes >> 7 >> 20 & 31)) << 3;
                V1_raw[2][1] = ((v1_bytes >> 7 >> 25 & 31)) << 3;
                
                uint64_t v2_bytes = *((uint64_t*)&src[texel_offset + 8]);
                V2_raw[0][0] = ((v2_bytes >> 5 >> 0 & 31));
                V2_raw[0][1] = ((v2_bytes >> 5 >> 5 & 31));
                V2_raw[1][0] = ((v2_bytes >> 5 >> 10 & 31));
                V2_raw[1][1] = ((v2_bytes >> 5 >> 15 & 31));
                V2_raw[2][0] = ((v2_bytes >> 5 >> 20 & 31));
                V2_raw[2][1] = ((v2_bytes >> 5 >> 25 & 31));
                
                S0_raw[0][0] = 255;
                S0_raw[0][1] = 255;
                S0_raw[1][0] = 255;
                S0_raw[1][1] = 255;
                S0_raw[2][0] = 255;
                S0_raw[2][1] = 255;
                
                uint32_t index_bytes = *((uint32_t*)&src[texel_offset + 12]);
                vector_index_bytes = (index_bytes >> 3) & (((uint32_t)(powl(2, 30)+0.5))-1);
                vector_index_precision = 2;
                scalar_index_bytes = vector_index_bytes;
                scalar_index_precision = vector_index_precision;
            } else if (mode == 3) {
                uint16_t partition_bytes = *((uint16_t*)&src[texel_offset + 0]);
                partition = partition_2_list[partition_bytes >> 4 & 63];
                anchor[1] = anchors[1][1][partition_bytes >> 4 & 63];
                anchor[2] = 16;
                
                uint16_t P_bytes = *((uint16_t*)&src[texel_offset + 11]);
                uint8_t P1 = P_bytes >> 6 & 1;
                uint8_t P2 = P_bytes >> 7 & 1;
                uint8_t P3 = P_bytes >> 8 & 1;
                uint8_t P4 = P_bytes >> 9 & 1;
                
                uint32_t v0_bytes = *((uint32_t*)&src[texel_offset + 1]);
                V0_raw[0][0] = ((v0_bytes >> 2 >> 0 & 127) << 1 | P1);
                V0_raw[0][1] = ((v0_bytes >> 2 >> 7 & 127) << 1 | P2);
                V0_raw[1][0] = ((v0_bytes >> 2 >> 14 & 127) << 1 | P3);
                V0_raw[1][1] = ((v0_bytes >> 2 >> 21 & 127) << 1 | P4);
                
                uint64_t v1_bytes = *((uint64_t*)&src[texel_offset + 4]);
                V1_raw[0][0] = ((v1_bytes >> 6 >> 0 & 127) << 1 | P1);
                V1_raw[0][1] = ((v1_bytes >> 6 >> 7 & 127) << 1 | P2);
                V1_raw[1][0] = ((v1_bytes >> 6 >> 14 & 127) << 1 | P3);
                V1_raw[1][1] = ((((v1_bytes >> 6 >> 21) & 127) << 1) | P4);
                
                uint32_t v2_bytes = *((uint32_t*)&src[texel_offset + 8]);
                V2_raw[0][0] = ((v2_bytes >> 2 >> 0 & 127) << 1 | P1);
                V2_raw[0][1] = ((v2_bytes >> 2 >> 7 & 127) << 1 | P2);
                V2_raw[1][0] = ((v2_bytes >> 2 >> 14 & 127) << 1 | P3);
                V2_raw[1][1] = ((v2_bytes >> 2 >> 21 & 127) << 1 | P4);
                
                S0_raw[0][0] = 255;
                S0_raw[0][1] = 255;
                S0_raw[1][0] = 255;
                S0_raw[1][1] = 255;
                
                uint64_t index_bytes = *((uint64_t*)&src[texel_offset + 8]);
                vector_index_bytes = (index_bytes >> 2+32) & (((uint64_t)(powl(2, 30)+0.5))-1);
                vector_index_precision = 2;
                scalar_index_bytes = vector_index_bytes;
                scalar_index_precision = vector_index_precision;
            } else if (mode == 4) {
                anchor[1] = 16;
                anchor[2] = 16;
                
                uint16_t rot_bytes = *((uint16_t*)&src[texel_offset + 0]);
                rot = rot_bytes >> 5 & 3;
                
                uint16_t idx_bytes = *((uint16_t*)&src[texel_offset + 0]);
                idx = idx_bytes >> 7 & 1;

                uint32_t v0_bytes = *((uint32_t*)&src[texel_offset + 1]);
                V0_raw[0][0] = ((v0_bytes >> 0 >> 0 & 31) << 3);
                V0_raw[0][1] = ((v0_bytes >> 0 >> 5 & 31) << 3);
                V0_raw[0][0] = V0_raw[0][0] | (V0_raw[0][0] >> 5);
                V0_raw[0][1] = V0_raw[0][1] | (V0_raw[0][1] >> 5);
                
                uint32_t v1_bytes = *((uint32_t*)&src[texel_offset + 2]);
                V1_raw[0][0] = ((v1_bytes >> 2 >> 0 & 31) << 3);
                V1_raw[0][1] = ((v1_bytes >> 2 >> 5 & 31) << 3);
                V1_raw[0][0] = V1_raw[0][0] | (V1_raw[0][0] >> 5);
                V1_raw[0][1] = V1_raw[0][1] | (V1_raw[0][1] >> 5);
                
                uint32_t v2_bytes = *((uint32_t*)&src[texel_offset + 3]);
                V2_raw[0][0] = ((v2_bytes >> 4 >> 0 & 31) << 3);
                V2_raw[0][1] = ((v2_bytes >> 4 >> 5 & 31) << 3);
                V2_raw[0][0] = V2_raw[0][0] | (V2_raw[0][0] >> 5);
                V2_raw[0][1] = V2_raw[0][1] | (V2_raw[0][1] >> 5);
                
                uint32_t s0_bytes = *((uint32_t*)&src[texel_offset + 4]);
                S0_raw[0][0] = ((s0_bytes >> 6 >> 0 & 63) << 2);
                S0_raw[0][1] = ((s0_bytes >> 6 >> 6 & 63) << 2);
                S0_raw[0][0] = S0_raw[0][0] | (S0_raw[0][0] >> 6);
                S0_raw[0][1] = S0_raw[0][1] | (S0_raw[0][1] >> 6);

                uint64_t first_index_bytes_raw = *((uint64_t*)&src[texel_offset + 6]);
                first_index_bytes_raw = (first_index_bytes_raw >> 2) & (((uint64_t)(powl(2, 31)+0.5))-1);
                uint64_t second_index_bytes_raw = *((uint64_t*)&src[texel_offset + 8]);
                second_index_bytes_raw = (second_index_bytes_raw >> 17) & (((uint64_t)(powl(2, 47)+0.5))-1);
                if (idx == 0) {
                    vector_index_bytes = first_index_bytes_raw;
                    vector_index_precision = 2;
                    scalar_index_bytes = second_index_bytes_raw;
                    scalar_index_precision = 3;
                } else {
                    vector_index_bytes = second_index_bytes_raw;
                    vector_index_precision = 3;
                    scalar_index_bytes = first_index_bytes_raw;
                    scalar_index_precision = 2;
                }
            } else if (mode == 5) {
                anchor[1] = 16;
                anchor[2] = 16;
                
                uint16_t rot_bytes = *((uint16_t*)&src[texel_offset + 0]);
                rot = rot_bytes >> 6 & 3;
                
                uint32_t v0_bytes = *((uint32_t*)&src[texel_offset + 1]);
                V0_raw[0][0] = ((v0_bytes >> 0 >> 0 & 127) << 1);
                V0_raw[0][1] = ((v0_bytes >> 0 >> 7 & 127) << 1);
                
                uint32_t v1_bytes = *((uint32_t*)&src[texel_offset + 2]);
                V1_raw[0][0] = ((v1_bytes >> 6 >> 0 & 127) << 1);
                V1_raw[0][1] = ((v1_bytes >> 6 >> 7 & 127) << 1);
                
                uint32_t v2_bytes = *((uint32_t*)&src[texel_offset + 4]);
                V2_raw[0][0] = ((v2_bytes >> 4 >> 0 & 127) << 1);
                V2_raw[0][1] = ((v2_bytes >> 4 >> 7 & 127) << 1);
                
                uint32_t s0_bytes = *((uint32_t*)&src[texel_offset + 6]);
                S0_raw[0][0] = ((s0_bytes >> 2 >> 0 & 255));
                S0_raw[0][1] = ((s0_bytes >> 2 >> 8 & 255));
                
                uint64_t vector_index_bytes_raw = *((uint64_t*)&src[texel_offset + 8]);
                vector_index_bytes = (vector_index_bytes_raw >> 2) & (((uint64_t)(powl(2, 31)+0.5))-1);
                vector_index_precision = 2;
                uint64_t scalar_index_bytes_raw = *((uint32_t*)&src[texel_offset + 12]);
                scalar_index_bytes = (scalar_index_bytes_raw >> 1) & (((uint32_t)(powl(2, 31)+0.5))-1);
                scalar_index_precision = 2;
                    
            } else if (mode == 6) {
                anchor[1] = 16;
                anchor[2] = 16;
                
                uint16_t P_bytes = *((uint16_t*)&src[texel_offset + 7]);
                uint8_t P1 = P_bytes >> 7 & 1;
                uint8_t P2 = P_bytes >> 8 & 1;
                
                uint32_t v0_bytes = *((uint32_t*)&src[texel_offset + 0]);
                V0_raw[0][0] = ((v0_bytes >> 7 >> 0 & 127) << 1 | P1);
                V0_raw[0][1] = ((v0_bytes >> 7 >> 7 & 127) << 1 | P2);
                
                uint32_t v1_bytes = *((uint32_t*)&src[texel_offset + 2]);
                V1_raw[0][0] = ((v1_bytes >> 5 >> 0 & 127) << 1 | P1);
                V1_raw[0][1] = ((v1_bytes >> 5 >> 7 & 127) << 1 | P2);
                
                uint32_t v2_bytes = *((uint32_t*)&src[texel_offset + 4]);
                V2_raw[0][0] = ((v2_bytes >> 3 >> 0 & 127) << 1 | P1);
                V2_raw[0][1] = ((v2_bytes >> 3 >> 7 & 127) << 1 | P2);
                
                uint32_t s0_bytes = *((uint32_t*)&src[texel_offset + 6]);
                S0_raw[0][0] = ((s0_bytes >> 1 >> 0 & 127) << 1 | P1);
                S0_raw[0][1] = ((s0_bytes >> 1 >> 7 & 127) << 1 | P2);
                
                uint64_t index_bytes = *((uint64_t*)&src[texel_offset + 8]);
                vector_index_bytes = (index_bytes >> 1) & (((uint64_t)(powl(2, 63)+0.5))-1);
                vector_index_precision = 4;
                scalar_index_bytes = vector_index_bytes;
                scalar_index_precision = vector_index_precision;
            } else if (mode == 7) {
                
                uint8_t partition_bytes = *((uint8_t*)&src[texel_offset + 1]);
                partition = partition_2_list[partition_bytes >> 0 & 63];
                anchor[1] = anchors[1][1][partition_bytes >> 0 & 63];
                anchor[2] = 16;
                
                uint16_t P_bytes = *((uint16_t*)&src[texel_offset + 11]);
                uint8_t P1 = P_bytes >> 6 & 1;
                uint8_t P2 = P_bytes >> 7 & 1;
                uint8_t P3 = P_bytes >> 8 & 1;
                uint8_t P4 = P_bytes >> 9 & 1;
                uint8_t color_component_precision = 6;
                
                uint32_t red_bytes = *((uint32_t*)&src[texel_offset + 1]);
                V0_raw[0][0] = ((red_bytes >> 6 >> 0 & 31) << 1 | P1) << (8-color_component_precision);
                V0_raw[0][1] = ((red_bytes >> 6 >> 5 & 31) << 1 | P2) << (8-color_component_precision);
                V0_raw[1][0] = ((red_bytes >> 6 >> 10 & 31) << 1 | P3) << (8-color_component_precision);
                V0_raw[1][1] = ((red_bytes >> 6 >> 15 & 31) << 1 | P4) << (8-color_component_precision);
                V0_raw[0][0] = V0_raw[0][0] | (V0_raw[0][0] >> color_component_precision);
                V0_raw[0][1] = V0_raw[0][1] | (V0_raw[0][1] >> color_component_precision);
                V0_raw[1][0] = V0_raw[1][0] | (V0_raw[1][0] >> color_component_precision);
                V0_raw[1][1] = V0_raw[1][1] | (V0_raw[1][1] >> color_component_precision);
                
                uint32_t green_bytes = *((uint32_t*)&src[texel_offset + 4]);
                V1_raw[0][0] = ((green_bytes >> 2 >> 0 & 31) << 1 | P1) << (8-color_component_precision);
                V1_raw[0][1] = ((green_bytes >> 2 >> 5 & 31) << 1 | P2) << (8-color_component_precision);
                V1_raw[1][0] = ((green_bytes >> 2 >> 10 & 31) << 1 | P3) << (8-color_component_precision);
                V1_raw[1][1] = ((green_bytes >> 2 >> 15 & 31) << 1 | P4) << (8-color_component_precision);
                V1_raw[0][0] = V1_raw[0][0] | (V1_raw[0][0] >> color_component_precision);
                V1_raw[0][1] = V1_raw[0][1] | (V1_raw[0][1] >> color_component_precision);
                V1_raw[1][0] = V1_raw[1][0] | (V1_raw[1][0] >> color_component_precision);
                V1_raw[1][1] = V1_raw[1][1] | (V1_raw[1][1] >> color_component_precision);
                
                
                uint32_t blue_bytes = *((uint32_t*)&src[texel_offset + 6]);
                V2_raw[0][0] = ((blue_bytes >> 6 >> 0 & 31) << 1 | P1) << (8-color_component_precision);
                V2_raw[0][1] = ((blue_bytes >> 6 >> 5 & 31) << 1 | P2) << (8-color_component_precision);
                V2_raw[1][0] = ((blue_bytes >> 6 >> 10 & 31) << 1 | P3) << (8-color_component_precision);
                V2_raw[1][1] = ((blue_bytes >> 6 >> 15 & 31) << 1 | P4) << (8-color_component_precision);
                V2_raw[0][0] = V2_raw[0][0] | (V2_raw[0][0] >> color_component_precision);
                V2_raw[0][1] = V2_raw[0][1] | (V2_raw[0][1] >> color_component_precision);
                V2_raw[1][0] = V2_raw[1][0] | (V2_raw[1][0] >> color_component_precision);
                V2_raw[1][1] = V2_raw[1][1] | (V2_raw[1][1] >> color_component_precision);
                
                uint32_t alpha_bytes = *((uint32_t*)&src[texel_offset + 9]);
                S0_raw[0][0] = ((alpha_bytes >> 2 >> 0 & 31) << 1 | P1) << (8-color_component_precision);
                S0_raw[0][1] = ((alpha_bytes >> 2 >> 5 & 31) << 1 | P2) << (8-color_component_precision);
                S0_raw[1][0] = ((alpha_bytes >> 2 >> 10 & 31) << 1 | P3) << (8-color_component_precision);
                S0_raw[1][1] = ((alpha_bytes >> 2 >> 15 & 31) << 1 | P4) << (8-color_component_precision);
                S0_raw[0][0] = S0_raw[0][0] | (S0_raw[0][0] >> color_component_precision);
                S0_raw[0][1] = S0_raw[0][1] | (S0_raw[0][1] >> color_component_precision);
                S0_raw[1][0] = S0_raw[1][0] | (S0_raw[1][0] >> color_component_precision);
                S0_raw[1][1] = S0_raw[1][1] | (S0_raw[1][1] >> color_component_precision);
                
                
                uint32_t index_bytes = *((uint32_t*)&src[texel_offset + 12]);
                vector_index_bytes = (index_bytes >> 2) & 1073741823;
                vector_index_precision = 2;
                scalar_index_bytes = vector_index_bytes;
                scalar_index_precision = vector_index_precision;
                
            }
            
            for (int pixel_y=0 ; pixel_y<4 ; ++pixel_y){
                for (int pixel_x=0 ; pixel_x<4 ; ++pixel_x){
                    uint8_t pixel_index = pixel_y*4 + pixel_x;
                    uint8_t subset = partition[pixel_index];
                    
                    uint8_t vector_index = 0;
                    uint8_t scalar_index = 0;
                    
                    uint8_t vector_index_offset = pixel_index*vector_index_precision;
                    uint8_t scalar_index_offset = pixel_index*scalar_index_precision;
                    if (pixel_index > anchor[0]) {
                        vector_index_offset -= 1;
                        scalar_index_offset -= 1;
                    }
                    if (pixel_index > anchor[1]) {
                        vector_index_offset -= 1;
                        scalar_index_offset -= 1;
                    }
                    if (pixel_index > anchor[2]) {
                        vector_index_offset -= 1;
                        scalar_index_offset -= 1;
                    }
                    if (pixel_index == anchor[0] || pixel_index == anchor[1] || pixel_index == anchor[2]) {
                        vector_index = ((vector_index_bytes >> vector_index_offset) & (((uint8_t)(powl(2, vector_index_precision-1)+0.5))-1));
                        scalar_index = ((scalar_index_bytes >> scalar_index_offset) & (((uint8_t)(powl(2, scalar_index_precision-1)+0.5))-1));
                    } else {
                        vector_index = ((vector_index_bytes >> vector_index_offset) & (((uint8_t)(powl(2, vector_index_precision)+0.5))-1));
                        scalar_index = ((scalar_index_bytes >> scalar_index_offset) & (((uint8_t)(powl(2, scalar_index_precision)+0.5))-1));
                    }
                    
                    uint8_t V0 = ((64 - palette_weights[vector_index_precision-2][vector_index])*(uint16_t)V0_raw[subset][0] + palette_weights[vector_index_precision-2][vector_index]*(uint16_t)V0_raw[subset][1] + 32) >> 6;
                    uint8_t V1 = ((64 - palette_weights[vector_index_precision-2][vector_index])*(uint16_t)V1_raw[subset][0] + palette_weights[vector_index_precision-2][vector_index]*(uint16_t)V1_raw[subset][1] + 32) >> 6;
                    uint8_t V2 = ((64 - palette_weights[vector_index_precision-2][vector_index])*(uint16_t)V2_raw[subset][0] + palette_weights[vector_index_precision-2][vector_index]*(uint16_t)V2_raw[subset][1] + 32) >> 6;
                    uint8_t S0 = ((64 - palette_weights[scalar_index_precision-2][scalar_index])*(uint16_t)S0_raw[subset][0] + palette_weights[scalar_index_precision-2][scalar_index]*(uint16_t)S0_raw[subset][1] + 32) >> 6;
                    
                    
                    if (rot == 0) {
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 0] = V0;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 1] = V1;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 2] = V2;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = S0;
                    } else if (rot == 1) {
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 0] = S0;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 1] = V1;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 2] = V2;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = V0;
                    } else if (rot == 2) {
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 0] = V0;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 1] = S0;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 2] = V2;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = V1;
                    } else if (rot == 3) {
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 0] = V0;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 1] = V1;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 2] = S0;
                        dst[(texel_y*4+pixel_y)*width*4 + (true_texel_x*4+pixel_x)*4 + 3] = V2;
                    }
                }
            }
        }
    }
    return 0;
}

EXPORT int read_r8(void* v_src, void* v_dst, uint32_t width, uint32_t height) {
    uint8_t* src = (uint8_t*) v_src;
    uint8_t* dst = (uint8_t*) v_dst;
//     #pragma omp parallel for schedule(static)
    for (int pixel_y=0 ; pixel_y<height ; ++pixel_y){
        for (int pixel_x=0 ; pixel_x<width ; ++pixel_x){
            dst[pixel_y*width*4 + pixel_x*4 + 0] = src[pixel_y*width + pixel_x];
            dst[pixel_y*width*4 + pixel_x*4 + 1] = 0;
            dst[pixel_y*width*4 + pixel_x*4 + 2] = 0;
            dst[pixel_y*width*4 + pixel_x*4 + 3] = 255;
        }
    }
    
    return 0;
}

EXPORT int read_r8g8(void* v_src, void* v_dst, uint32_t width, uint32_t height) {
    uint8_t* src = (uint8_t*) v_src;
    uint8_t* dst = (uint8_t*) v_dst;
//     #pragma omp parallel for schedule(static)
    for (int pixel_y=0 ; pixel_y<height ; ++pixel_y){
        for (int pixel_x=0 ; pixel_x<width ; ++pixel_x){
            dst[pixel_y*width*4 + pixel_x*4 + 0] = src[pixel_y*width*2 + pixel_x*2 + 0];
            dst[pixel_y*width*4 + pixel_x*4 + 1] = src[pixel_y*width*2 + pixel_x*2 + 1];
            dst[pixel_y*width*4 + pixel_x*4 + 2] = 0;
            dst[pixel_y*width*4 + pixel_x*4 + 3] = 255;
        }
    }
    
    return 0;
}

EXPORT int read_r8g8b8a8(void* v_src, void* v_dst, uint32_t width, uint32_t height) {
    uint8_t* src = (uint8_t*) v_src;
    uint8_t* dst = (uint8_t*) v_dst;
//     #pragma omp parallel for schedule(static)
    for (int pixel_y=0 ; pixel_y<height ; ++pixel_y){
        for (int pixel_x=0 ; pixel_x<width ; ++pixel_x){
            dst[pixel_y*width*4 + pixel_x*4 + 0] = src[pixel_y*width*4 + pixel_x*4 + 0];
            dst[pixel_y*width*4 + pixel_x*4 + 1] = src[pixel_y*width*4 + pixel_x*4 + 1];
            dst[pixel_y*width*4 + pixel_x*4 + 2] = src[pixel_y*width*4 + pixel_x*4 + 2];
            dst[pixel_y*width*4 + pixel_x*4 + 3] = src[pixel_y*width*4 + pixel_x*4 + 3];
        }
    }
    
    return 0;
}

