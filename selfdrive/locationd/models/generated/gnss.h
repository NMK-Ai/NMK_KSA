#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_4149634754144377149);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_707842066181839936);
void gnss_H_mod_fun(double *state, double *out_4622199009918465762);
void gnss_f_fun(double *state, double dt, double *out_440379023002144509);
void gnss_F_fun(double *state, double dt, double *out_1861880544798438541);
void gnss_h_6(double *state, double *sat_pos, double *out_4937302933359892922);
void gnss_H_6(double *state, double *sat_pos, double *out_335184189587978812);
void gnss_h_20(double *state, double *sat_pos, double *out_7228795566902431221);
void gnss_H_20(double *state, double *sat_pos, double *out_3459799581926243952);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_827149192473234528);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_2859790614318727918);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_827149192473234528);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_2859790614318727918);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}