def plot_hubble_fig( fitter='both', datfilename='data/distances/hubblefig.dat'):
    from pytools import plotsetup, colorpalette as cp
    from astropy.io import ascii
    import numpy as np
    from scipy import optimize as scopt
    from matplotlib import pyplot as pl
    from matplotlib import ticker
    import os
    import sys

    dmint_mlcs=0.08 # intrinsic scatter in SNIa luminosities for MLCS2k2 (Jha:2007)
    dmint_salt=0.08 # intrinsic scatter in SNIa luminosities for SALT2 (Conley:2011)

    zTomas = 1.31#,1.35]
    zerrTomas = 0.01#,0.02]
    dmTomas_mlcs = 44.06#,44.22]
    dmerrTomas_mlcs = np.sqrt(0.09**2 + dmint_mlcs**2)
    dmTomas_salt = 44.09#,44.19]
    dmerrTomas_salt = np.sqrt(0.16**2 + dmint_salt**2)

    thisfile = sys.argv[0]
    if 'ipython' in thisfile :
        thisfile = __file__
    thisdir = os.path.dirname( os.path.abspath(thisfile))

    datfile = os.path.join( thisdir, datfilename )
    hubbledat = ascii.read( datfile, format='commented_header', header_start=-1, data_start=0)
    z = hubbledat['z']
    dm_mlcs = hubbledat['dm_mlcs']
    dm_mlcs_err = np.sqrt(hubbledat['dm_mlcs_err']**2 + dmint_mlcs**2)
    dm_salt = hubbledat['dm_salt']
    dm_salt_err = np.sqrt(hubbledat['dm_salt_err']**2 + dmint_salt**2)
    iscp = np.where( hubbledat['survey']=='scp')
    igoods = np.where( hubbledat['survey']=='goods')
    fig = plotsetup.halfpaperfig( )
    pl.clf()
    if fitter.lower()=='both':
        ax1 = fig.add_subplot(2,1,1)
        ax2 = fig.add_subplot(2,1,2, sharex=ax1, sharey=ax1)
    elif fitter.lower().startswith('mlcs') :
        ax1 = fig.add_subplot(1,1,1)
        ax2 = ax1
    elif fitter.lower().startswith('salt') :
        ax1 = fig.add_subplot(1,1,1)
        ax2 = ax1

    if fitter.lower()[:5] in ['both','mlcs'] :
        ax1.errorbar( z[igoods], dm_mlcs[igoods], dm_mlcs_err[igoods], ls=' ', marker='s', capsize=0, color=cp.lightgrey, ecolor=cp.darkgrey )
        ax1.errorbar( z[iscp], dm_mlcs[iscp], dm_mlcs_err[iscp], ls=' ', marker='o', capsize=0, color=cp.lightgrey, ecolor=cp.darkgrey )
        ax1.errorbar( zTomas, dmTomas_mlcs, dmerrTomas_mlcs, zerrTomas, marker='D',
                      color=cp.teal, capsize=0, ls=' ')

    if fitter.lower()[:5] in ['both','salt'] :
        ax2.errorbar( z[igoods], dm_salt[igoods], dm_salt_err[igoods], ls=' ', marker='s', capsize=0, color=cp.lightgrey, ecolor=cp.darkgrey )
        ax2.errorbar( z[iscp], dm_salt[iscp], dm_salt_err[iscp], ls=' ', marker='o', capsize=0, color=cp.lightgrey, ecolor=cp.darkgrey )
        ax2.errorbar( zTomas, dmTomas_salt, dmerrTomas_salt, zerrTomas, marker='D',
                      color=cp.teal, capsize=0, ls=' ' )    #ax.text( 0.05,0.95, 'Riess et al. 2007', ha='left', va='top', color=cp.black, fontsize='small' , transform=ax.transAxes )

    # ax1.set_xlabel( "Redshift")
    ax2.set_xlabel( "Redshift")
    # ax.xaxis.set_label_coords( -0.05, -0.03)
    ax1.xaxis.set_major_locator( ticker.MultipleLocator( 0.1 ) )
    ax1.xaxis.set_minor_locator( ticker.MultipleLocator( 0.05 ) )
    ax2.xaxis.set_major_locator( ticker.MultipleLocator( 0.1 ) )
    ax2.xaxis.set_minor_locator( ticker.MultipleLocator( 0.05 ) )

    # dm_mlcs = slope * z - intercept
    def line( x, slope, intercept ):
        return slope*(x-1.31) + intercept

    lineparam0 = np.array([1,45])
    fit_mlcs, cov_mlcs = scopt.curve_fit( line, z, dm_mlcs, lineparam0, dm_mlcs_err)
    fit_salt, cov_salt = scopt.curve_fit( line, z, dm_salt, lineparam0, dm_salt_err)

    for ax,fittername,fit,cov,dmTom,dmerrTom,dmint,color in zip(
            [ax1,ax2],['MLCS2k2','SALT2'],
            [fit_mlcs,fit_salt],[cov_mlcs,cov_salt],
            [dmTomas_mlcs,dmTomas_salt],
            [dmerrTomas_mlcs,dmerrTomas_salt],
            [dmint_mlcs,dmint_salt],
            [cp.blue,cp.darkred]):
        if fitter.lower().startswith('mlcs') and fittername!='MLCS2k2' : continue
        if fitter.lower().startswith('salt') and fittername!='SALT2' : continue
        slope, intercept  = fit
        slope_err, intercept_err = np.sqrt( np.diagonal(cov) )
        fit_string = r'dm$_{\rm %s} = (%.2f\pm%.2f)(z-1.31)+(%.2f\pm%.2f)$'%(
            fittername, round(slope,2),round(slope_err,2),
            round(intercept,2),round(intercept_err,2) )

        zfit = np.arange(0.9,1.8,0.01)
        dmfit =  slope*(zfit-1.31) + intercept
        a =  (slope+slope_err)*(zfit-1.31) + intercept+intercept_err
        b =  (slope+slope_err)*(zfit-1.31) + intercept-intercept_err
        c =  (slope-slope_err)*(zfit-1.31) + intercept+intercept_err
        d =  (slope-slope_err)*(zfit-1.31) + intercept-intercept_err

        top = np.max( np.array([a,b,c,d]), axis=0)
        bot = np.min( np.array([a,b,c,d]), axis=0)
        ax.plot( zfit, dmfit, color='0.5',ls='-')
        ax.fill_between( zfit, bot, top, color='0.5',alpha=0.3)

        deltam_mu = intercept-dmTom
        deltam_mu_err = np.sqrt( dmerrTom**2 + intercept_err**2 + dmint**2 )

        mu = 10**(0.4*(deltam_mu))
        muerr = mu * deltam_mu_err / 1.0857

        mu_string = r'$\mu_{\rm obs} = %.2f\pm%.2f \ \ (%.2f\pm%.2f$ mag)'%(
            round(mu,2),round(muerr,2),
            round(deltam_mu,2), round(deltam_mu_err,2) )

        ax.plot( [zTomas,zTomas], [dmTom+dmerrTom,intercept],
                 ls=':', color=color )
        ax.plot(  [1.27,1.31], [43.95,dmTom+deltam_mu/3.],
                  ls='-', lw=0.5, color=color )

        if fitter=='both':
            ax.text( 0.04,0.92, fit_string ,ha='left', va='top',
                     color=color, transform=ax.transAxes, fontsize='small' )
            ax.set_ylabel( "%s Dist. Mod."%fittername)
            ax.text( 1.20,43.75, mu_string, color=color, fontsize='small')
        else :
            ax.text( 0.04, 0.92, 'Unlensed SNIa', color='0.3', fontsize='small',
                     ha='left', va='top',transform=ax.transAxes )
            ax.text( 1.33, 44.05, 'SN Tomas', color=cp.teal,fontsize='small',
                     ha='left', va='bottom')
            ax.text( 1.16,43.65, mu_string, color=color, fontsize='small')


    # muTomas, muerrTomas = 44.1385, 0.0753
    # muerrtot = np.sqrt( muerrTomas**2 + 0.1**2)

    #ax.text( 0.05,0.9, 'Suzuki et al. 2012', ha='left', va='top', color=cp.green, fontsize='small', transform=ax.transAxes )


    ax1.set_xlim( 1.12, 1.44 )
    ax1.set_ylim( 43.51, 45.99 )
    fig.subplots_adjust( left=0.15, bottom=0.13, right=0.95, top=0.95, hspace=0)
    if fitter!='both':
        ax.set_ylabel('Dist. Mod.')
        fig.subplots_adjust( left=0.2, bottom=0.16, right=0.95, top=0.95, hspace=0)
        ax2.set_xlabel( "Redshift:")
        ax.xaxis.set_label_coords( -0.06, -0.05)
        ax1.set_ylim( 43.52, 45.98 )


    pl.draw()


