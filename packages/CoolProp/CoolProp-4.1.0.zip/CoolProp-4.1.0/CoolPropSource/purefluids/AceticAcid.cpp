#include "CoolProp.h"
#include <vector>
#include "CPExceptions.h"
#include "FluidClass.h"
#include "AceticAcid.h"
#include "Solvers.h"

/// A stub class to do the density(T,p) calculations for near the critical point using Brent solver
class DensityTpResids : public FuncWrapper1D
{
private:
	double p,T;
	Fluid *pFluid;
public:
	DensityTpResids(Fluid *pFluid, double T, double p){this->pFluid = pFluid; this->p = p; this->T = T;};
	~DensityTpResids(){};
	
	double call(double rho)
	{
		return this->p - pFluid->pressure_Trho(T,rho);
	}
};

AceticAcidClass::AceticAcidClass()
{
	double n[] = {0, -0.15624834164583e1, -0.874703669570960e0, 0.46968858010355e1, 0.97367136204905e-2, -0.49055972708048e-2, 0.24499997808125e2, -0.31443235067567e2, -0.13768156877983e1, 0.14849435860881e1, 0.11374909453775e1, -0.26039791873344e1, -0.30484923493199e-1, 0.53316386834696e1, -0.56733952193640e1, -0.126785566440530e0};
	double d[] = {0, 1, 1, 2, 2, 6, 3, 3, 3, 4, 4, 5, 5, 5, 5, 2};
	double t[] = {0, -1.000, 1.375, 1.000, 1.375, 0.750, -0.250, 0.000, 2.250, 0.125, 2.125, 1.250, 2.250, 2.125, 2.375, 14.000};
	double l[] = {0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3};

    // Critical parameters
    crit.rho = 351;
    crit.T = 590.70;
    crit.v = 1.0/crit.rho;

    // Other fluid parameters
    params.molemass = 60.05196;
    params.Ttriple = 289.8;
	params.ptriple = _HUGE;
    params.accentricfactor = _HUGE;
    params.R_u = 8.314472;

    // Limits of EOS
	limits.Tmin = params.Ttriple;
    limits.Tmax = 500.0;
    limits.pmax = 100000.0;
    limits.rhomax = 1000000.0*params.molemass;

	// Residual part
    phirlist.push_back(new phir_power(n,d,t,l,1,15,16));
	double m = 1.01871348, vbarn = 0.444215309e-1,kappabar = 0.109117041e-4 , epsilonbar = 12.2735737;
	phirlist.push_back(new phir_SAFT_associating_1(m, epsilonbar, vbarn, kappabar));

	// Ideal-gas part
	phi0list.push_back(new phi0_lead(-3.94616949, 5.48487930));
	phi0list.push_back(new phi0_logtau(3.66766530));
	phi0list.push_back(new phi0_power(-0.210687796, -1));
	phi0list.push_back(new phi0_power(-0.781330239, -2));
	phi0list.push_back(new phi0_power(0.130979005, -3));
	phi0list.push_back(new phi0_Planck_Einstein( 6.28891793, 2.09502491));

	// Set the critical pressure based on the evaluation of the EOS
	reduce = crit;
	crit.p = PressureUnit(pressure_Trho(crit.T,crit.rho+1e-10), UNIT_PA);

    name.assign("AceticAcid");
    aliases.push_back(std::string("ACETICACID"));
    REFPROPname.assign("ACETIC");

	BibTeXKeys.EOS = "Piazza-FPE-2011";
	BibTeXKeys.SURFACE_TENSION = "Mulero-JPCRD-2012";

	double Tt = params.Ttriple;
	double Tc = crit.T;
	double pc = crit.p.Pa;

	double w = 6.67228479e-09*Tc*Tc*Tc-7.20464352e-06*Tc*Tc+3.16947758e-03*Tc-2.88760012e-01;
	double q = -6.08930221451*w -5.42477887222;
	double pt = exp(q*(Tc/Tt-1))*pc;

	if (1)
	{
		double rhoL,rhoV;

		std::string errstr;
		double T = params.Ttriple;
		double p0 = pt;
		double gibbsL,gibbsV;
		double rhoLstore = _HUGE;
		for (double rho = crit.rho; rho < crit.rho*7; rho += crit.rho/5)
		{
			DensityTpResids DTPR = DensityTpResids(this,T,p0);
			std::string errstr;
			try{
				rhoL = density_Tp(T,p0,rho);
				gibbsL = gibbs_Trho(T,rhoL);
				double pp = pressure_Trho(T,rhoL);
				if (dpdrho_Trho(T,rhoL)>0){
					rhoLstore = rhoL;
				};
				double rr = 0;
			}
			catch (std::exception &)
			{
			}
		}
		double rhoVstore = _HUGE;
		for (double rho = crit.rho; rho > 1e-16; rho /= 1.5)
		{
			try{
				rhoV = density_Tp(T,p0,rho);
				double pp = pressure_Trho(T,rhoV);
				gibbsV = gibbs_Trho(T,rhoV);
				if (dpdrho_Trho(T,rhoV)>0){
					rhoVstore = rhoV;
				};
				double rr = 0;
			}
			catch (std::exception &)
			{
			}
		}
		double p;
		rhoL = rhoLstore; rhoV = rhoVstore;
		FILE *fp;
		fp = fopen("aceticancillary.csv","w");
		fclose(fp);
		while (T < Tc)
		{
			if (T>486)
			{
				rhosatPure_Akasaka(T, &rhoL, &rhoV, &p, 0.1, true);
			}
			else
			{
				rhosatPure(T, &rhoL, &rhoV, &p, 1.0, true);
			}
			fp = fopen("aceticancillary.csv","a+");
			fprintf(fp,"%g,%g,%g,%g\n", T, p, rhoL, rhoV);
			fclose(fp);
			if (T < 580)
			{
				T += 1;
			}
			else
			{
				T += 0.001;
			}
		}
		fclose(fp);
		double rr = 0;
	}
}

double AceticAcidClass::psat(double T)
{
	throw NotImplementedError();
	// Max error is  0.0991069278587 % between 175.61 and 512.5999 K
    const double t[] = {0, 0.077, 0.3505, 0.3515, 0.3555, 0.3645, 0.371, 0.383, 4.833333333333333, 5.0, 10.166666666666666};
    const double N[] = {0, -9.7405903858600631, 3260402084.5156689, -4777161923.1118717, 2016877532.0827882, -811371244.62298751, 338648069.09319597, -27394516.566426165, -46.888287588943143, 46.324153446741605, -3.5670972200405648};
    double summer = 0, theta;
    theta = 1 - T/crit.T;
    for (int i=1; i<=10; i++)
    {
        summer += N[i]*pow(theta, t[i]);
    }
    return crit.p.Pa*exp(crit.T/T*summer);
}

double AceticAcidClass::rhosatL(double T)
{
	throw NotImplementedError();
	// Max error is  0.0821373889953 % between 175.61 and 512.4999 K	
    const double t[] = {0, 0.052000000000000005, 0.359, 0.362, 0.3725, 0.38999999999999996, 0.39149999999999996, 1.5, 6.333333333333333};
    const double N[] = {0, 0.78895468490910248, -430749.82813271997, 688983.70332109113, -408037.75579782907, 951810.28685599519, -802005.68894233427, 1.3144166962003807, 0.62507823719120026};
    double summer=0,theta;
    theta = 1 - T/crit.T;
	for (int i=1; i <= 8; i++)
	{
		summer += N[i]*pow(theta,t[i]);
	}
	return crit.rho*(summer+1);
}

double AceticAcidClass::rhosatV(double T)
{
	throw NotImplementedError();
	// Max error is  0.236163723479 % between 175.61 and 512.4999 K
    const double t[] = {0, 0.14100000000000001, 0.352, 0.361, 0.363, 0.3645, 0.365, 0.385, 4.0};
    const double N[] = {0, -177.86155125251409, 826168404.02091146, -73665853180.39566, 307970330692.74481, -666652930848.13257, 431587738673.01379, -65453571.459690347, -2.5772990424534554};
    double summer=0,theta;
    theta=1-T/reduce.T;	
	for (int i=1; i<=8; i++)
	{
		summer += N[i]*pow(theta,t[i]);
	}
	return reduce.rho*exp(reduce.T/T*summer);
}
//double AceticAcidClass::surface_tension_T(double T)
//{
//	// Mulero, JPCRD 2012
//	return 0.22421*pow(1-T/reduce.T,1.3355) - 0.21408*pow(1-T/reduce.T,1.677) + 0.083233*pow(1-T/reduce.T,4.4402);
//}
