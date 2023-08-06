# amplilyzer.graphics
# (c) Sven Rahmann, 2011--2013

"""
This module provides plotting routines for amplikyzer.
It does not implement a subcommand.
"""

import sys

#########################################################
# safe import of plotting library

_FORMAT = None  # global memory of format during initial import

def import_pyplot_with_format(format):    
    """
    import matplotlib with a format-specific backend;
    globally set 'mpl' and 'plt' module variables.
    """
    if _FORMAT is None:
        _import_matplotlib(format)  # globally sets plt = matplotplib.pyplot
    if format != _FORMAT:
        raise RuntimeError(
            "Cannot use different formats ({}/{}) in the same run.\nPlease restart amplikyzer.".format(_FORMAT, format))

def _import_matplotlib(format):
    global np, mpl, plt
    BACKENDS = dict(png='Agg', pdf='Agg', svg='svg')
    # using 'pdf' (instead of 'Agg') for pdf results in strange %-symbols
    import numpy as np
    import matplotlib as mpl
    mpl.use(BACKENDS[format])
    import matplotlib.pyplot as plt
    global _FORMAT
    _FORMAT = format


#########################################################
# individual methylation plot

def plot_individual(analysis, fname, format="pdf", style="color", options=None):
    """
    Create and save an individual methylation plot.
    analysis:  an instance of methylation.MethylationAnalysis
    fname:     filename of the resulting image file
    format:    image format (e.g., 'png', 'pdf', 'svg')
    style:     image style ('color' or 'bw')
    options:   options dictionary with the following keys:
      showpositions (True: show CpG positions, else ranks).
    """
    import_pyplot_with_format(format)
    m, n = analysis.nrows, analysis.ncols
    if options is None:  options = dict()

    # treat showpositions option
    cpgpos = analysis.cpg_positions
    posstr = "positions"
    if not options["showpositions"]:
        cpgpos = list(range(1,len(cpgpos)+1))
        posstr = "ranks"

    # determine colormap        
    if style ==  "color":
        colors = ["#3333ee", "#777777", "#cc4444"]  # (blue -> red)
    else:
        colors = ["#ffffff", "#000000"]
    mycolormap = mpl.colors.LinearSegmentedColormap.from_list("mycolormap", colors)
    
    # initialize figure, set figure title/remark and axis title (subtitle)
    fig = plt.figure()
    titles = ["Methylation Analysis: " + analysis.title]
    yheight = 0.8
    if analysis.remark is not None:
        titles.append(analysis.remark)
        yheight = 0.77
    subtitles = ["{} reads, {} CpGs, {:.1%} methylation".format(
        m, n, analysis.total_meth_rate)]
    title = "\n".join(titles)
    subtitle = "\n".join(subtitles)
    fig.suptitle(title, fontsize=14)
    ax = fig.add_axes([0.05, 0.1, 0.9, yheight]) # left, bottom, width, height
    ax.set_title(subtitle, fontsize=12)

    # plot image
    array = analysis.as_matrix()
    ax.imshow(array, cmap=mycolormap,
        interpolation='none', origin='upper', vmin=0.0, vmax=1.0)
    ax.set_aspect('auto')
    
    # column-wise methylation rates
    xfontsize = 8 if n < 25 else 6
    x1labels = ["{:.0f}".format(100*m) for m in analysis.cpg_meth_rates]
    x2labels = ["{:d}".format(pos) for pos in cpgpos]
    xlabels = [x1+"\n"+x2 for x1,x2 in zip(x1labels,x2labels)]    
    ax.set_xlabel('methylation rates [%] / {} of CpGs'.format(posstr))
    ax.set_xticks(range(n))
    ax.set_xticklabels(xlabels, fontsize=xfontsize)
    ax.set_ylabel('individual reads')
    ax.set_yticks([])  # no yticks

    # save to file
    if fname == "-": fname = sys.stdout
    fig.savefig(fname, format=format)  # bbox_inches="tight" cuts off title!
    plt.close(fig)
    fig = None
    return True


#########################################################
# comparative methylation plot

def plot_comparative(analysis, fname, format="pdf", style="color", options=None):
    """
    Create and save a comparative methylation plot.
    analysis: an instance of methylation.ComparativeAnalysis
    fname: filename of the resulting image file
    format: image format (e.g., 'png', 'pdf', 'svg')
    style: image style ('color' or 'bw')
    Return True if successful, False when CpGs are inconsistent.
    """
    if options is None:  options = dict()

    # determine cpg positions or ranks
    cpgpos = analysis.cpg_positions
    if cpgpos is None:  return False  # inconsistent CpGs
    posstr = "positions"
    if not options["showpositions"]:
        cpgpos = list(range(1,len(cpgpos)+1))
        posstr = "ranks"
    
    m, n = analysis.shape
    assert n is not None
    import_pyplot_with_format(format)

    # determine colormap        
    if style ==  "color":
        colors = ["#4444dd", "#dd4444"]  # (blue -> red)
        fontcolor = lambda x: "#ffffff"
    else:
        colors = ["#ffffff", "#000000"]  # (white -> black)
        fontcolor = lambda x: "#ffffff" if x>0.5 else "#000000"
    mycolormap = mpl.colors.LinearSegmentedColormap.from_list("mycolormap", colors)

    # initialize figure, set figure title/remark and axis title (subtitle)
    fig = plt.figure()
    titles = ["Comparative Analysis: " + analysis.title]
    yheight = 0.8
    if analysis.remark is not None:
        titles.append(analysis.remark)
        yheight = 0.77
    subtitles = ["{} samples, {} CpGs".format(m, n)]
    title = "\n".join(titles)
    subtitle = "\n".join(subtitles)
    fig.suptitle(title, fontsize=14, x=0.54)
    # if there is not enough space for labels at the left side,
    # increase the 'left' coordinate and reduce the 'width' in the following line
    ax = fig.add_axes([0.14, 0.1, 0.84, yheight]) # left, bottom, width, height    
    ax.set_title(subtitle, fontsize=12)

    # plot image
    array = np.array(analysis.as_matrix())
    image = ax.imshow(array, cmap=mycolormap,
        interpolation='none', origin='upper', vmin=0.0, vmax=1.0)
    ax.set_aspect('auto')
    for i in range(m):
        for j in range(n):
            x = array[i,j]
            ax.text(j,i, "{:3.0f}".format(x*100), fontsize=8, color=fontcolor(x), ha='center')
    
    # column-wise methylation rates
    avgcolrates = np.mean(array, axis=0)
    xfontsize = 8 if n < 20 else 6
    x1labels = ["{:.0f}".format(100*m) for m in avgcolrates]
    x2labels = ["{:d}".format(pos) for pos in cpgpos]
    xlabels = [x1+"\n"+x2 for x1,x2 in zip(x1labels,x2labels)]    
    ax.set_xlabel('average methylation rates [%] / {} of CpGs'.format(posstr))
    ax.set_xticks(range(n))
    ax.set_xticklabels(xlabels, fontsize=xfontsize)
    y1labels = list(analysis.sample_names())
    y2labels = [ "{:.1f} ({:d})".format(100 * s.total_meth_rate, s.nreads)
                 for s in analysis._samples ]
    ylabels = [y1+"\n"+y2 for y1,y2 in zip(y1labels,y2labels)]
    ax.set_yticks(range(m))
    yfontsize = 8 if m < 21 else 6
    ax.set_yticklabels(ylabels, fontsize=yfontsize)

    # save to file
    if fname == "-":  fname = sys.stdout
    fig.savefig(fname, format=format)  # bbox_inches="tight" cuts off title!
    plt.close(fig)
    fig = None
    return True
