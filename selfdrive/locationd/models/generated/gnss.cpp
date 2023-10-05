#include "gnss.h"

namespace {
#define DIM 11
#define EDIM 11
#define MEDIM 11
typedef void (*Hfun)(double *, double *, double *);
const static double MAHA_THRESH_6 = 3.8414588206941227;
const static double MAHA_THRESH_20 = 3.8414588206941227;
const static double MAHA_THRESH_7 = 3.8414588206941227;
const static double MAHA_THRESH_21 = 3.8414588206941227;

/******************************************************************************
 *                       Code generated with SymPy 1.12                       *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_4149634754144377149) {
   out_4149634754144377149[0] = delta_x[0] + nom_x[0];
   out_4149634754144377149[1] = delta_x[1] + nom_x[1];
   out_4149634754144377149[2] = delta_x[2] + nom_x[2];
   out_4149634754144377149[3] = delta_x[3] + nom_x[3];
   out_4149634754144377149[4] = delta_x[4] + nom_x[4];
   out_4149634754144377149[5] = delta_x[5] + nom_x[5];
   out_4149634754144377149[6] = delta_x[6] + nom_x[6];
   out_4149634754144377149[7] = delta_x[7] + nom_x[7];
   out_4149634754144377149[8] = delta_x[8] + nom_x[8];
   out_4149634754144377149[9] = delta_x[9] + nom_x[9];
   out_4149634754144377149[10] = delta_x[10] + nom_x[10];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_707842066181839936) {
   out_707842066181839936[0] = -nom_x[0] + true_x[0];
   out_707842066181839936[1] = -nom_x[1] + true_x[1];
   out_707842066181839936[2] = -nom_x[2] + true_x[2];
   out_707842066181839936[3] = -nom_x[3] + true_x[3];
   out_707842066181839936[4] = -nom_x[4] + true_x[4];
   out_707842066181839936[5] = -nom_x[5] + true_x[5];
   out_707842066181839936[6] = -nom_x[6] + true_x[6];
   out_707842066181839936[7] = -nom_x[7] + true_x[7];
   out_707842066181839936[8] = -nom_x[8] + true_x[8];
   out_707842066181839936[9] = -nom_x[9] + true_x[9];
   out_707842066181839936[10] = -nom_x[10] + true_x[10];
}
void H_mod_fun(double *state, double *out_4622199009918465762) {
   out_4622199009918465762[0] = 1.0;
   out_4622199009918465762[1] = 0;
   out_4622199009918465762[2] = 0;
   out_4622199009918465762[3] = 0;
   out_4622199009918465762[4] = 0;
   out_4622199009918465762[5] = 0;
   out_4622199009918465762[6] = 0;
   out_4622199009918465762[7] = 0;
   out_4622199009918465762[8] = 0;
   out_4622199009918465762[9] = 0;
   out_4622199009918465762[10] = 0;
   out_4622199009918465762[11] = 0;
   out_4622199009918465762[12] = 1.0;
   out_4622199009918465762[13] = 0;
   out_4622199009918465762[14] = 0;
   out_4622199009918465762[15] = 0;
   out_4622199009918465762[16] = 0;
   out_4622199009918465762[17] = 0;
   out_4622199009918465762[18] = 0;
   out_4622199009918465762[19] = 0;
   out_4622199009918465762[20] = 0;
   out_4622199009918465762[21] = 0;
   out_4622199009918465762[22] = 0;
   out_4622199009918465762[23] = 0;
   out_4622199009918465762[24] = 1.0;
   out_4622199009918465762[25] = 0;
   out_4622199009918465762[26] = 0;
   out_4622199009918465762[27] = 0;
   out_4622199009918465762[28] = 0;
   out_4622199009918465762[29] = 0;
   out_4622199009918465762[30] = 0;
   out_4622199009918465762[31] = 0;
   out_4622199009918465762[32] = 0;
   out_4622199009918465762[33] = 0;
   out_4622199009918465762[34] = 0;
   out_4622199009918465762[35] = 0;
   out_4622199009918465762[36] = 1.0;
   out_4622199009918465762[37] = 0;
   out_4622199009918465762[38] = 0;
   out_4622199009918465762[39] = 0;
   out_4622199009918465762[40] = 0;
   out_4622199009918465762[41] = 0;
   out_4622199009918465762[42] = 0;
   out_4622199009918465762[43] = 0;
   out_4622199009918465762[44] = 0;
   out_4622199009918465762[45] = 0;
   out_4622199009918465762[46] = 0;
   out_4622199009918465762[47] = 0;
   out_4622199009918465762[48] = 1.0;
   out_4622199009918465762[49] = 0;
   out_4622199009918465762[50] = 0;
   out_4622199009918465762[51] = 0;
   out_4622199009918465762[52] = 0;
   out_4622199009918465762[53] = 0;
   out_4622199009918465762[54] = 0;
   out_4622199009918465762[55] = 0;
   out_4622199009918465762[56] = 0;
   out_4622199009918465762[57] = 0;
   out_4622199009918465762[58] = 0;
   out_4622199009918465762[59] = 0;
   out_4622199009918465762[60] = 1.0;
   out_4622199009918465762[61] = 0;
   out_4622199009918465762[62] = 0;
   out_4622199009918465762[63] = 0;
   out_4622199009918465762[64] = 0;
   out_4622199009918465762[65] = 0;
   out_4622199009918465762[66] = 0;
   out_4622199009918465762[67] = 0;
   out_4622199009918465762[68] = 0;
   out_4622199009918465762[69] = 0;
   out_4622199009918465762[70] = 0;
   out_4622199009918465762[71] = 0;
   out_4622199009918465762[72] = 1.0;
   out_4622199009918465762[73] = 0;
   out_4622199009918465762[74] = 0;
   out_4622199009918465762[75] = 0;
   out_4622199009918465762[76] = 0;
   out_4622199009918465762[77] = 0;
   out_4622199009918465762[78] = 0;
   out_4622199009918465762[79] = 0;
   out_4622199009918465762[80] = 0;
   out_4622199009918465762[81] = 0;
   out_4622199009918465762[82] = 0;
   out_4622199009918465762[83] = 0;
   out_4622199009918465762[84] = 1.0;
   out_4622199009918465762[85] = 0;
   out_4622199009918465762[86] = 0;
   out_4622199009918465762[87] = 0;
   out_4622199009918465762[88] = 0;
   out_4622199009918465762[89] = 0;
   out_4622199009918465762[90] = 0;
   out_4622199009918465762[91] = 0;
   out_4622199009918465762[92] = 0;
   out_4622199009918465762[93] = 0;
   out_4622199009918465762[94] = 0;
   out_4622199009918465762[95] = 0;
   out_4622199009918465762[96] = 1.0;
   out_4622199009918465762[97] = 0;
   out_4622199009918465762[98] = 0;
   out_4622199009918465762[99] = 0;
   out_4622199009918465762[100] = 0;
   out_4622199009918465762[101] = 0;
   out_4622199009918465762[102] = 0;
   out_4622199009918465762[103] = 0;
   out_4622199009918465762[104] = 0;
   out_4622199009918465762[105] = 0;
   out_4622199009918465762[106] = 0;
   out_4622199009918465762[107] = 0;
   out_4622199009918465762[108] = 1.0;
   out_4622199009918465762[109] = 0;
   out_4622199009918465762[110] = 0;
   out_4622199009918465762[111] = 0;
   out_4622199009918465762[112] = 0;
   out_4622199009918465762[113] = 0;
   out_4622199009918465762[114] = 0;
   out_4622199009918465762[115] = 0;
   out_4622199009918465762[116] = 0;
   out_4622199009918465762[117] = 0;
   out_4622199009918465762[118] = 0;
   out_4622199009918465762[119] = 0;
   out_4622199009918465762[120] = 1.0;
}
void f_fun(double *state, double dt, double *out_440379023002144509) {
   out_440379023002144509[0] = dt*state[3] + state[0];
   out_440379023002144509[1] = dt*state[4] + state[1];
   out_440379023002144509[2] = dt*state[5] + state[2];
   out_440379023002144509[3] = state[3];
   out_440379023002144509[4] = state[4];
   out_440379023002144509[5] = state[5];
   out_440379023002144509[6] = dt*state[7] + state[6];
   out_440379023002144509[7] = dt*state[8] + state[7];
   out_440379023002144509[8] = state[8];
   out_440379023002144509[9] = state[9];
   out_440379023002144509[10] = state[10];
}
void F_fun(double *state, double dt, double *out_1861880544798438541) {
   out_1861880544798438541[0] = 1;
   out_1861880544798438541[1] = 0;
   out_1861880544798438541[2] = 0;
   out_1861880544798438541[3] = dt;
   out_1861880544798438541[4] = 0;
   out_1861880544798438541[5] = 0;
   out_1861880544798438541[6] = 0;
   out_1861880544798438541[7] = 0;
   out_1861880544798438541[8] = 0;
   out_1861880544798438541[9] = 0;
   out_1861880544798438541[10] = 0;
   out_1861880544798438541[11] = 0;
   out_1861880544798438541[12] = 1;
   out_1861880544798438541[13] = 0;
   out_1861880544798438541[14] = 0;
   out_1861880544798438541[15] = dt;
   out_1861880544798438541[16] = 0;
   out_1861880544798438541[17] = 0;
   out_1861880544798438541[18] = 0;
   out_1861880544798438541[19] = 0;
   out_1861880544798438541[20] = 0;
   out_1861880544798438541[21] = 0;
   out_1861880544798438541[22] = 0;
   out_1861880544798438541[23] = 0;
   out_1861880544798438541[24] = 1;
   out_1861880544798438541[25] = 0;
   out_1861880544798438541[26] = 0;
   out_1861880544798438541[27] = dt;
   out_1861880544798438541[28] = 0;
   out_1861880544798438541[29] = 0;
   out_1861880544798438541[30] = 0;
   out_1861880544798438541[31] = 0;
   out_1861880544798438541[32] = 0;
   out_1861880544798438541[33] = 0;
   out_1861880544798438541[34] = 0;
   out_1861880544798438541[35] = 0;
   out_1861880544798438541[36] = 1;
   out_1861880544798438541[37] = 0;
   out_1861880544798438541[38] = 0;
   out_1861880544798438541[39] = 0;
   out_1861880544798438541[40] = 0;
   out_1861880544798438541[41] = 0;
   out_1861880544798438541[42] = 0;
   out_1861880544798438541[43] = 0;
   out_1861880544798438541[44] = 0;
   out_1861880544798438541[45] = 0;
   out_1861880544798438541[46] = 0;
   out_1861880544798438541[47] = 0;
   out_1861880544798438541[48] = 1;
   out_1861880544798438541[49] = 0;
   out_1861880544798438541[50] = 0;
   out_1861880544798438541[51] = 0;
   out_1861880544798438541[52] = 0;
   out_1861880544798438541[53] = 0;
   out_1861880544798438541[54] = 0;
   out_1861880544798438541[55] = 0;
   out_1861880544798438541[56] = 0;
   out_1861880544798438541[57] = 0;
   out_1861880544798438541[58] = 0;
   out_1861880544798438541[59] = 0;
   out_1861880544798438541[60] = 1;
   out_1861880544798438541[61] = 0;
   out_1861880544798438541[62] = 0;
   out_1861880544798438541[63] = 0;
   out_1861880544798438541[64] = 0;
   out_1861880544798438541[65] = 0;
   out_1861880544798438541[66] = 0;
   out_1861880544798438541[67] = 0;
   out_1861880544798438541[68] = 0;
   out_1861880544798438541[69] = 0;
   out_1861880544798438541[70] = 0;
   out_1861880544798438541[71] = 0;
   out_1861880544798438541[72] = 1;
   out_1861880544798438541[73] = dt;
   out_1861880544798438541[74] = 0;
   out_1861880544798438541[75] = 0;
   out_1861880544798438541[76] = 0;
   out_1861880544798438541[77] = 0;
   out_1861880544798438541[78] = 0;
   out_1861880544798438541[79] = 0;
   out_1861880544798438541[80] = 0;
   out_1861880544798438541[81] = 0;
   out_1861880544798438541[82] = 0;
   out_1861880544798438541[83] = 0;
   out_1861880544798438541[84] = 1;
   out_1861880544798438541[85] = dt;
   out_1861880544798438541[86] = 0;
   out_1861880544798438541[87] = 0;
   out_1861880544798438541[88] = 0;
   out_1861880544798438541[89] = 0;
   out_1861880544798438541[90] = 0;
   out_1861880544798438541[91] = 0;
   out_1861880544798438541[92] = 0;
   out_1861880544798438541[93] = 0;
   out_1861880544798438541[94] = 0;
   out_1861880544798438541[95] = 0;
   out_1861880544798438541[96] = 1;
   out_1861880544798438541[97] = 0;
   out_1861880544798438541[98] = 0;
   out_1861880544798438541[99] = 0;
   out_1861880544798438541[100] = 0;
   out_1861880544798438541[101] = 0;
   out_1861880544798438541[102] = 0;
   out_1861880544798438541[103] = 0;
   out_1861880544798438541[104] = 0;
   out_1861880544798438541[105] = 0;
   out_1861880544798438541[106] = 0;
   out_1861880544798438541[107] = 0;
   out_1861880544798438541[108] = 1;
   out_1861880544798438541[109] = 0;
   out_1861880544798438541[110] = 0;
   out_1861880544798438541[111] = 0;
   out_1861880544798438541[112] = 0;
   out_1861880544798438541[113] = 0;
   out_1861880544798438541[114] = 0;
   out_1861880544798438541[115] = 0;
   out_1861880544798438541[116] = 0;
   out_1861880544798438541[117] = 0;
   out_1861880544798438541[118] = 0;
   out_1861880544798438541[119] = 0;
   out_1861880544798438541[120] = 1;
}
void h_6(double *state, double *sat_pos, double *out_4937302933359892922) {
   out_4937302933359892922[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + state[6];
}
void H_6(double *state, double *sat_pos, double *out_335184189587978812) {
   out_335184189587978812[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_335184189587978812[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_335184189587978812[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_335184189587978812[3] = 0;
   out_335184189587978812[4] = 0;
   out_335184189587978812[5] = 0;
   out_335184189587978812[6] = 1;
   out_335184189587978812[7] = 0;
   out_335184189587978812[8] = 0;
   out_335184189587978812[9] = 0;
   out_335184189587978812[10] = 0;
}
void h_20(double *state, double *sat_pos, double *out_7228795566902431221) {
   out_7228795566902431221[0] = sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2)) + sat_pos[3]*state[10] + state[6] + state[9];
}
void H_20(double *state, double *sat_pos, double *out_3459799581926243952) {
   out_3459799581926243952[0] = (-sat_pos[0] + state[0])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3459799581926243952[1] = (-sat_pos[1] + state[1])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3459799581926243952[2] = (-sat_pos[2] + state[2])/sqrt(pow(-sat_pos[0] + state[0], 2) + pow(-sat_pos[1] + state[1], 2) + pow(-sat_pos[2] + state[2], 2));
   out_3459799581926243952[3] = 0;
   out_3459799581926243952[4] = 0;
   out_3459799581926243952[5] = 0;
   out_3459799581926243952[6] = 1;
   out_3459799581926243952[7] = 0;
   out_3459799581926243952[8] = 0;
   out_3459799581926243952[9] = 1;
   out_3459799581926243952[10] = sat_pos[3];
}
void h_7(double *state, double *sat_pos_vel, double *out_827149192473234528) {
   out_827149192473234528[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_7(double *state, double *sat_pos_vel, double *out_2859790614318727918) {
   out_2859790614318727918[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[6] = 0;
   out_2859790614318727918[7] = 1;
   out_2859790614318727918[8] = 0;
   out_2859790614318727918[9] = 0;
   out_2859790614318727918[10] = 0;
}
void h_21(double *state, double *sat_pos_vel, double *out_827149192473234528) {
   out_827149192473234528[0] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + (sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2)) + state[7];
}
void H_21(double *state, double *sat_pos_vel, double *out_2859790614318727918) {
   out_2859790614318727918[0] = pow(sat_pos_vel[0] - state[0], 2)*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[3] - state[3])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[1] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[1] - state[1])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[1] - state[1], 2)*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[4] - state[4])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[2] = (sat_pos_vel[0] - state[0])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[3] - state[3])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + (sat_pos_vel[1] - state[1])*(sat_pos_vel[2] - state[2])*(sat_pos_vel[4] - state[4])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) + pow(sat_pos_vel[2] - state[2], 2)*(sat_pos_vel[5] - state[5])/pow(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2), 3.0/2.0) - (sat_pos_vel[5] - state[5])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[3] = -(sat_pos_vel[0] - state[0])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[4] = -(sat_pos_vel[1] - state[1])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[5] = -(sat_pos_vel[2] - state[2])/sqrt(pow(sat_pos_vel[0] - state[0], 2) + pow(sat_pos_vel[1] - state[1], 2) + pow(sat_pos_vel[2] - state[2], 2));
   out_2859790614318727918[6] = 0;
   out_2859790614318727918[7] = 1;
   out_2859790614318727918[8] = 0;
   out_2859790614318727918[9] = 0;
   out_2859790614318727918[10] = 0;
}
#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;

  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);

  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H);

  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();


    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;

  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);

  // update cov
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}




}
extern "C" {

void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_6, H_6, NULL, in_z, in_R, in_ea, MAHA_THRESH_6);
}
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_20, H_20, NULL, in_z, in_R, in_ea, MAHA_THRESH_20);
}
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_7, H_7, NULL, in_z, in_R, in_ea, MAHA_THRESH_7);
}
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_21, H_21, NULL, in_z, in_R, in_ea, MAHA_THRESH_21);
}
void gnss_err_fun(double *nom_x, double *delta_x, double *out_4149634754144377149) {
  err_fun(nom_x, delta_x, out_4149634754144377149);
}
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_707842066181839936) {
  inv_err_fun(nom_x, true_x, out_707842066181839936);
}
void gnss_H_mod_fun(double *state, double *out_4622199009918465762) {
  H_mod_fun(state, out_4622199009918465762);
}
void gnss_f_fun(double *state, double dt, double *out_440379023002144509) {
  f_fun(state,  dt, out_440379023002144509);
}
void gnss_F_fun(double *state, double dt, double *out_1861880544798438541) {
  F_fun(state,  dt, out_1861880544798438541);
}
void gnss_h_6(double *state, double *sat_pos, double *out_4937302933359892922) {
  h_6(state, sat_pos, out_4937302933359892922);
}
void gnss_H_6(double *state, double *sat_pos, double *out_335184189587978812) {
  H_6(state, sat_pos, out_335184189587978812);
}
void gnss_h_20(double *state, double *sat_pos, double *out_7228795566902431221) {
  h_20(state, sat_pos, out_7228795566902431221);
}
void gnss_H_20(double *state, double *sat_pos, double *out_3459799581926243952) {
  H_20(state, sat_pos, out_3459799581926243952);
}
void gnss_h_7(double *state, double *sat_pos_vel, double *out_827149192473234528) {
  h_7(state, sat_pos_vel, out_827149192473234528);
}
void gnss_H_7(double *state, double *sat_pos_vel, double *out_2859790614318727918) {
  H_7(state, sat_pos_vel, out_2859790614318727918);
}
void gnss_h_21(double *state, double *sat_pos_vel, double *out_827149192473234528) {
  h_21(state, sat_pos_vel, out_827149192473234528);
}
void gnss_H_21(double *state, double *sat_pos_vel, double *out_2859790614318727918) {
  H_21(state, sat_pos_vel, out_2859790614318727918);
}
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
}

const EKF gnss = {
  .name = "gnss",
  .kinds = { 6, 20, 7, 21 },
  .feature_kinds = {  },
  .f_fun = gnss_f_fun,
  .F_fun = gnss_F_fun,
  .err_fun = gnss_err_fun,
  .inv_err_fun = gnss_inv_err_fun,
  .H_mod_fun = gnss_H_mod_fun,
  .predict = gnss_predict,
  .hs = {
    { 6, gnss_h_6 },
    { 20, gnss_h_20 },
    { 7, gnss_h_7 },
    { 21, gnss_h_21 },
  },
  .Hs = {
    { 6, gnss_H_6 },
    { 20, gnss_H_20 },
    { 7, gnss_H_7 },
    { 21, gnss_H_21 },
  },
  .updates = {
    { 6, gnss_update_6 },
    { 20, gnss_update_20 },
    { 7, gnss_update_7 },
    { 21, gnss_update_21 },
  },
  .Hes = {
  },
  .sets = {
  },
  .extra_routines = {
  },
};

ekf_init(gnss);
