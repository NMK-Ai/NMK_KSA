#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_7671772380488357646);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6415244549961512941);
void car_H_mod_fun(double *state, double *out_4793324406912704184);
void car_f_fun(double *state, double dt, double *out_4336982717214696753);
void car_F_fun(double *state, double dt, double *out_305298039477594138);
void car_h_25(double *state, double *unused, double *out_4724499269242857974);
void car_H_25(double *state, double *unused, double *out_194523981305357563);
void car_h_24(double *state, double *unused, double *out_9001274178621341536);
void car_H_24(double *state, double *unused, double *out_3363401617496965573);
void car_h_30(double *state, double *unused, double *out_3038765987577814467);
void car_H_30(double *state, double *unused, double *out_2323808977201891064);
void car_h_26(double *state, double *unused, double *out_7758632912820402807);
void car_H_26(double *state, double *unused, double *out_3936027300179413787);
void car_h_27(double *state, double *unused, double *out_4257469902763982791);
void car_H_27(double *state, double *unused, double *out_149045665401466153);
void car_h_29(double *state, double *unused, double *out_7275222149140415997);
void car_H_29(double *state, double *unused, double *out_2834040321516283248);
void car_h_28(double *state, double *unused, double *out_744203364896862854);
void car_H_28(double *state, double *unused, double *out_2248358695553247326);
void car_h_31(double *state, double *unused, double *out_8977336828006571131);
void car_H_31(double *state, double *unused, double *out_4562235402412765263);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}