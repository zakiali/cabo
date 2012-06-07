#! /usr/bin/env python
import aipy as a, numpy as n, pylab as plt
import sys, ephem, optparse

o = optparse.OptionParser()
o.set_description(__doc__)
a.scripting.add_standard_options(o, cal=True, src=True)
o.add_option('-p', dest='plot', action='store_true',
    help='plot the data in the two .npz files or not. specify the file names if option is given with the -f option. .') 
o.add_option('-f', '--files', dest='files', type='str', 
    help='files to plot in -p option is given.file name distinguished by a _.')
opts, args = o.parse_args(sys.argv[1:])


print opts.plot
if opts.plot:
    if opts.files == None:
        print 'specify filenames.'
        exit() 

deg2rad = n.pi/180.
rad2deg = 180/n.pi
if not opts.plot:

    sources,cutoff,catalog = a.scripting.parse_srcs(opts.src, opts.cat)
    colors = ['b','g','r','c','m','y','k','w']
    if not ('Sun' in sources):
        sources.append('Sun') # default source. 
    sdf = .5/1024.

    freqs = n.arange(1024)*sdf + (sdf + .5) # IN GHz
    #set up observer.
    aa = a.cal.get_aa(opts.cal,freqs)
    cat = a.cal.get_catalog(opts.cal, sources, cutoff, catalog)
    sun = ephem.Sun() # default source
    ad = {}
    ad['sources'] = []
    for src in sources:
        ad[src+'az'] = []
        ad[src+'alt'] = []
        ad[src+'ra'] = []
        ad[src+'dec'] = []
        ad[src+'times'] = []
        ad['sources'].append(src)

    for file in args:
        print 'processing  %s'%file
        uvi = a.miriad.UV(file)
        #just need to pick one baseline b/c we want all times. 
        uvi.select('antennae',0,0)
        for p,d,f in uvi.all(raw=True): 
            crd, t, (i,j) = p 
            aa.set_jultime(t)
            for src in sources:
                currsrc = cat[src]
                currsrc.compute(aa)
                ad[src+'times'].append(t)
                ad[src+'az'].append(currsrc.az)
                ad[src+'alt'].append(currsrc.alt)
                ad[src+'ra'].append(currsrc.ra)
                ad[src+'dec'].append(currsrc.dec)
    #       print sun.ra, sun.dec 

    for s in cat.keys():
        for key in ['az','alt','ra','dec','times']:
            ad[s+key] = n.array(ad[s+key])

    print 'Saving data to ->',str(ad[src+'times'][0])+'.npz'
    n.savez(str(ad[src+'times'][0])+'.npz', **ad)

if opts.plot:
    if opts.files.find('_') != -1:
        f1,f2 = opts.files.split('_')
        d1 = n.load(f1) 
        d2 = n.load(f2) 
        for num,src in enumerate(d1['sources']):
            print src
            fig = plt.figure(num)
            fig.text(0.5,0.975,'%s'%src)         
            plt.subplot(211)
            plt.title('az vs. alt')
            plt.xlabel('az')
            plt.ylabel('alt')
            plt.plot(d1[src+'az']*rad2deg,d1[src+'alt']*rad2deg,'.b',d2[src+'az']*rad2deg,d2[src+'alt']*rad2deg,'.r')
            plt.subplot(212)
            plt.title('ra vs. dec')
            plt.xlabel('ra')
            plt.ylabel('dec')
            plt.plot(d1[src+'ra'],d1[src+'dec'],'.b',d2[src+'ra'],d2[src+'dec'],'.r')
    else: 
        f = opts.files
        d = n.load(f)
        for num,src in enumerate(d['sources']):
            fig = plt.figure(num)
            fig.text(0.5,0.975,'%s'%src)         
            plt.subplot(211)
            plt.title('az vs. alt')
            plt.xlabel('az')
            plt.ylabel('alt')
            plt.plot(d[src+'az']*rad2deg,d[src+'alt']*rad2deg,'.b')
            plt.subplot(212)
            plt.title('ra vs. dec')
            plt.xlabel('ra')
            plt.ylabel('dec')
            plt.plot(d[src+'ra'],d[src+'dec'],'.b')
    plt.show()
