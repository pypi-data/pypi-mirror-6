import getopt,sys,re,logging,math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from brewer2mpl import diverging
import scipy.spatial
import scipy.cluster
import cockatoo
from cockatoo.cli.exceptions import Usage
from ete2 import Tree

logger = logging.getLogger(__name__)

DEND_PALETTE = [
                '#8E0152', '#C51B7D', '#DE77AE', '#F1B6DA', 
                '#A6DBA0', '#5AAE61', '#1B7837', '#00441B', 
                '#F4A582', '#D6604D', '#B2182B', '#67001F', 
                '#542788', '#2166AC', '#4393C3', '#92C5DE', 
                '#B2ABD2', '#8073AC', '#053061', '#2D004B', 
                '#003C30', '#01665E', '#35978F', '#80CDC1',
                '#FEE08B', '#D9EF8B', '#FDAE61', '#A6D96A', 
                ]

def run(argv):
    try:
        opts, args = getopt.getopt(argv[1:], "vpdnts:w:b:c:", ["verbose", "pdist", "dendrogram", "newick", "testing", "screen=", "weights=", "basename=", "cutoff="])
    except getopt.error, msg:
        raise Usage(msg)

    screen_file = None
    output_pdist = False
    output_dendrogram = False
    output_newick = False
    weights = [1,1]
    base_name = 'cockatoo-out'
    verbose = False
    testing = False
    cutoff_pct = 0.7
    for o, a in opts:
        if o in ("-s", "--screen"):
            screen_file = a
        elif o in ("-p", "--pdist"):
            output_pdist = True
        elif o in ("-d", "--dendrogram"):
            output_dendrogram = True
        elif o in ("-n", "--newick"):
            output_newick = True
        elif o in ("-c", "--cutoff"):
            try:
                cutoff_pct = float(a)
            except:
                raise Usage("Please provide an float for the cutoff")
        elif o in ("-w", "--weights"):
            weights = []
            for w in re.split(r',', a):
                try:
                    weights.append(float(w))
                except:
                    raise Usage("Invalid weights")
        elif o in ("-b", "--basename"):
            base_name = a
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-t", "--testing"):
            testing = True

    if screen_file is None:
        raise Usage("Please provide a path to the screen")
    if len(base_name) == 0:
        raise Usage("Please provide a basename")
    if len(weights) != 2:
        raise Usage("Please provide a valid weights string: 1,1")

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Parsing screen..")
    screen = cockatoo.screen.parse_json(screen_file)

    _cluster(screen, weights, cutoff_pct, base_name, output_pdist, output_dendrogram, output_newick, testing)

    return 0

def _pdist(screen, weights):
    logger.info("Computing pairwise distances...")
    cocktails = np.array(screen.cocktails)
    m = len(cocktails)
    dm = np.zeros((m * (m - 1)) / 2, dtype=np.double)
    k = 0
    for i in xrange(0, m - 1):
        for j in xrange(i + 1, m):
            dm[k] = cockatoo.metric.distance(cocktails[i], cocktails[j], weights)
            k = k + 1

    return dm

def _cluster(screen, weights, cutoff_pct, base_name, output_pdist=False, output_dendrogram=False, output_newick=False, testing=False):
    dm = _pdist(screen, weights)
    logger.info("Performing hierarichal clustering...")

    if testing:
        logger.info("TESTING CLUSTERING METHODS...")
        with open('hclust-test-linkage-results.csv', 'w') as out:
            out.write("\t".join(['method', 'coph_coeff', 'max_dist', 'cutoff', 'nclusters', 'wss', 'bss', 'silhouette']))
            out.write("\n")
            for method in ['complete', 'average', 'weighted']:
                Z = scipy.cluster.hierarchy.linkage(dm, method=method, metric='euclidean')
                (c,d) = scipy.cluster.hierarchy.cophenet(Z, Y=dm)
                logger.info("Cophenetic correlation coefficient for '%s': %s" % (method,c))
                max_dist = max(Z[:,2])
                cutoff = cutoff_pct*max_dist
                clusters = list(scipy.cluster.hierarchy.fcluster(Z,t=cutoff, criterion='distance'))
                (nclusters, wss,bss) = _compute_sse(screen, clusters, weights)
                sil_coeff = _compute_silhouette(screen, clusters, weights)
                out.write("\t".join([method, str(c), str(max_dist), str(cutoff), str(nclusters), str(wss), str(bss), str(sil_coeff)]))
                out.write("\n")
        return

    Z = scipy.cluster.hierarchy.linkage(dm, method='average', metric='euclidean')
    (c,d) = scipy.cluster.hierarchy.cophenet(Z, Y=dm)
    logger.info("Cophenetic correlation coefficient: %s" % (str(c)))
    max_dist = max(Z[:,2])
    cutoff = cutoff_pct*max_dist
    logger.info("Max cophenetic distance found: %s" % (str(max_dist)))
    logger.info("Using cophenetic distance cutoff: %s" % (str(cutoff)))
    clusters = list(scipy.cluster.hierarchy.fcluster(Z,t=cutoff, criterion='distance'))
    (nclusters, wss,bss) = _compute_sse(screen, clusters, weights)
    sil_coeff = _compute_silhouette(screen, clusters, weights)
    logger.info("Clusters: %s" % str(nclusters))
    logger.info("WSS: %s" % str(wss))
    logger.info("BSS: %s" % str(bss))
    logger.info("Silhouette coeff: %s" % str(sil_coeff))

    if output_pdist:
        _write_pdist(dm, base_name)
        _write_heatmap(dm, cutoff, base_name)
    if output_dendrogram:
        _write_dendrogram_heat(dm, Z, cutoff, clusters, base_name)
        _write_dendrogram(dm, Z, cutoff, base_name)
    if output_newick:
        _write_newick(Z, base_name)

    _write_clusters(screen, clusters, base_name)

def _write_pdist(dm, base_name):
    logger.info("Writing pair wise distances...")
    fname = "%s.pdist" % base_name
    with open(fname, 'w') as out:
        out.write("\t".join(['i','j','distance']))
        out.write("\n")
        v = scipy.spatial.distance.squareform(dm)
        (m,n) = v.shape
        for i in xrange(0, m):
            for j in xrange(0, n):
                out.write("\t".join([str(i), str(j), str(v[i][j])]))
                out.write("\n")

def _write_heatmap(dm, cutoff, base_name):
    logger.info("Writing heatmap...")
    fname = "%s.heatmap.png" % base_name
    mpl.rcParams.update({'font.size': 22})
    plt.clf()
    fig = plt.figure(figsize=(12,12))
    v = scipy.spatial.distance.squareform(dm)

    (n,m) = v.shape
    plt.pcolormesh(v, cmap=diverging.RdBu['max'].get_mpl_colormap())
    plt.xlim(xmax=n)
    plt.ylim(ymax=m)
    plt.clim(0,1)
    plt.colorbar()
    plt.tight_layout()

    fig.savefig(fname)

def _write_dendrogram_heat(dm, Z, cutoff, clusters, base_name):
    logger.info("Writing dendrogram...")
    fname = "%s.dendrogram-heatmap.png" % base_name
    plt.clf()

    # Heatmap colors
    heat_cmap = diverging.RdBu['max'].get_mpl_colormap()
    norm = mpl.colors.Normalize(vmin=0, vmax=1)

    scipy.cluster.hierarchy.set_link_color_palette(DEND_PALETTE)

    fig = plt.figure(figsize=(12,12))
    padding_w = 0.025

    # Axis for left dendrogram
    left_dend_x, left_dend_y, left_dend_w, left_dend_h = 0.05,0.22,0.2,0.6
    
    # Axis for heatmap
    heat_x = (left_dend_x + left_dend_w) + padding_w
    heat_y = left_dend_y;
    heat_w = 0.5
    heat_h = left_dend_h

    # Axis for top dendrogram
    top_dend_x = (left_dend_x + left_dend_w) + padding_w 
    top_dend_y = left_dend_y + left_dend_h
    top_dend_w = 0.5
    top_dend_h = 0.15


    top_dend_axis = fig.add_axes(
        (top_dend_x, top_dend_y, top_dend_w, top_dend_h), 
        frame_on=False
    )

    scipy.cluster.hierarchy.dendrogram(Z, no_labels=True, show_leaf_counts=False, color_threshold=cutoff)
    plt.axhline(y=cutoff, linestyle='--', color='#000000')
    top_dend_axis.set_xticks([])
    top_dend_axis.set_yticks([])

    left_dend_axis = fig.add_axes(
        ((left_dend_x+padding_w), left_dend_y, left_dend_w, left_dend_h), 
        frame_on=False
    )

    ddata = scipy.cluster.hierarchy.dendrogram(
        Z, orientation='right', no_labels=True, 
        show_leaf_counts=False,color_threshold=cutoff
    )
    plt.axvline(x=cutoff, linestyle='--', color='#000000')

    left_dend_axis.set_xticks([])
    left_dend_axis.set_yticks([])

    heat_axis = fig.add_axes((heat_x, heat_y, heat_w, heat_h))

    v = scipy.spatial.distance.squareform(dm)
    idx = ddata['leaves']
    v = v[:,idx]
    v = v[idx,:]
    im = heat_axis.matshow(v, aspect='auto', origin='lower', cmap=heat_cmap, norm=norm)
    heat_axis.set_xticks([])
    heat_axis.set_yticks([])

    # Color scale
    cb_axis = fig.add_axes([0.07, 0.88, 0.18, 0.02], frame_on=False)
    cb = mpl.colorbar.ColorbarBase(cb_axis, cmap=heat_cmap, orientation='horizontal', ticks=[0,0.5,1])
    cb_axis.set_title("simliarity score")

    plt.savefig(fname)

def _write_dendrogram(dm, Z, cutoff, base_name):
    logger.info("Writing dendrogram...")
    fname = "%s.dendrogram.png" % base_name
    scipy.cluster.hierarchy.set_link_color_palette(DEND_PALETTE)

    plt.clf()
    ddata = scipy.cluster.hierarchy.dendrogram(
       Z, orientation='right', no_labels=True, show_leaf_counts=False,color_threshold=cutoff
   )

    plt.axvline(x=cutoff, linestyle='--', color='#000000')
    plt.savefig(fname)

def _write_newick(Z, base_name):
    logger.info("Writing newick...")
    fname = "%s.newick" % base_name
    # Output newick
    T = scipy.cluster.hierarchy.to_tree(Z)
    root = Tree()
    root.dist = 0
    root.name = "root"
    item2node = {T: root}
    to_visit = [T]
    while to_visit:
        node = to_visit.pop()
        cl_dist = node.dist /2.0
        for ch_node in [node.left, node.right]:
            if ch_node:
                ch = Tree()
                ch.dist = cl_dist
                if ch_node.left is None and ch_node.right is None:
                    nlabel = ch_node.id
                    nlabel += 1
                    ch.name = str(nlabel)
                else:
                    ch.name = ''
                item2node[node].add_child(ch)
                item2node[ch_node] = ch
                to_visit.append(ch_node)

    tree = root
    tree.write(format=1, outfile=fname)

def _write_clusters(screen, clusters, base_name):
    logger.info("Writing cluster assignments...")
    fname = "%s.clusters" % base_name
    with open(fname, 'w') as out:
        out.write("cluster\tcocktail\tid\n")
        for i,v in enumerate(clusters):
            out.write("%s\t%s\t%s" % (v, screen.cocktails[i].name,str(i)))
            out.write("\n")

def _compute_sse(screen, clusters, weights):
    idx_map = {}
    for i,v in enumerate(clusters):
        idx_map[v] = idx_map.get(v, [])
        idx_map[v].append(i)

    wss = 0
    bss = 0
    means = {}
    for cl, rec in idx_map.iteritems():
        m = len(rec)
        if m > 1:
            dm = np.zeros((m * (m - 1)) // 2, dtype=np.double)
            k = 0
            for i in xrange(0, m - 1):
                for j in xrange(i + 1, m):
                    i_idx = rec[i]
                    j_idx = rec[j]
                    dm[k] = cockatoo.metric.distance(screen.cocktails[i_idx], screen.cocktails[j_idx], weights=weights)
                    k = k + 1

            mean = dm.mean()
            means[cl] = mean
            for i in xrange(0, k):
                wss += math.pow(dm[i] - mean, 2)

    mean_arr = np.array(means.values())
    mean = mean_arr.mean()
    for cl, rec in idx_map.iteritems():
        m = len(rec)
        if cl in means:
            c_mean = means[cl]
            bss += m * math.pow(c_mean-mean, 2)

    return (len(idx_map), wss, bss)

def _compute_silhouette(screen, clusters, weights):
    idx_map = {}
    for i,v in enumerate(clusters):
        idx_map[v] = idx_map.get(v, [])
        idx_map[v].append(i)

    S = np.zeros(len(clusters), dtype=np.double)
    k = 0
    for i,v in enumerate(clusters):
        # a(i) = average distance within cluster
        a_i = _average_dist(screen, i, idx_map[v], weights)

        # b(i) = average distance outside cluster
        outside_dists = []
        for vv in idx_map:
            if v == vv: continue
            outside_dists.append(_average_dist(screen, i, idx_map[vv], weights))
        
        b = np.array(outside_dists)
        b_i = b.min()

        S[k] = float(b_i-a_i)/max(a_i, b_i)
        k += 1

    return S.mean()


def _average_dist(screen, i, idx, weights):
    dists = []
    for x in idx:
        if x != i:
            dists.append(cockatoo.metric.distance(screen.cocktails[i], screen.cocktails[x], weights=weights))

    if len(dists) > 0:
        d = np.array(dists)
        return d.mean()

    return 0

def synopsis():
    return "perform hierarchical clustering on a screen"

def options():
    return """
    -v, --verbose            print debugging output
    -s, --screen             screen
    -p, --pdist              output pairwise distances
    -d, --dendrogram         output dendrogram
    -n, --newick             output dendrogram in newick format
    -b, --basename           basename for output files
    -w, --weights            weights=1,1
    -c, --cutoff             percent of max cophenetic distance to use as cutoff
    """
