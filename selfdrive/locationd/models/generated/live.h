#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_3527272168916747465);
void live_err_fun(double *nom_x, double *delta_x, double *out_6045848623961905122);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7169558580725911560);
void live_H_mod_fun(double *state, double *out_2233486417319465898);
void live_f_fun(double *state, double dt, double *out_394989617356335065);
void live_F_fun(double *state, double dt, double *out_4258683105057258686);
void live_h_4(double *state, double *unused, double *out_630004665006177454);
void live_H_4(double *state, double *unused, double *out_2557128699668065886);
void live_h_9(double *state, double *unused, double *out_305682243973039777);
void live_H_9(double *state, double *unused, double *out_2315939053038475241);
void live_h_10(double *state, double *unused, double *out_3290065580213621136);
void live_H_10(double *state, double *unused, double *out_5952593910960601130);
void live_h_12(double *state, double *unused, double *out_4778882070426826303);
void live_H_12(double *state, double *unused, double *out_2462327708363895909);
void live_h_35(double *state, double *unused, double *out_5254255709407145805);
void live_H_35(double *state, double *unused, double *out_5207890740688909618);
void live_h_32(double *state, double *unused, double *out_2690950986992451521);
void live_H_32(double *state, double *unused, double *out_7437548960813029440);
void live_h_13(double *state, double *unused, double *out_2838899766990680185);
void live_H_13(double *state, double *unused, double *out_6243414584483540250);
void live_h_14(double *state, double *unused, double *out_305682243973039777);
void live_H_14(double *state, double *unused, double *out_2315939053038475241);
void live_h_33(double *state, double *unused, double *out_7133213938072286658);
void live_H_33(double *state, double *unused, double *out_8358447745327767222);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}