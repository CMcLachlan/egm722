import numpy as np
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from shapely.geometry.polygon import Polygon
from cartopy.feature import ShapelyFeature
import matplotlib.patches as mpatches


def percentile_stretch(img, pmin=0., pmax=100.):
    '''
    This is where you should write a docstring.
    '''
    # here, we make sure that pmin < pmax, and that they are between 0, 100
    if not 0 <= pmin < pmax <= 100:
        raise ValueError('0 <= pmin < pmax <= 100')
    # here, we make sure that the image is only 2-dimensional
    if not img.ndim == 2:
        raise ValueError('Image can only have two dimensions (row, column)')

    minval = np.percentile(img, pmin)
    maxval = np.percentile(img, pmax)

    stretched = (img - minval) / (maxval - minval)  # stretch the image to 0, 1
    stretched[img < minval] = 0  # set anything less than minval to the new minimum, 0.
    stretched[img > maxval] = 1  # set anything greater than maxval to the new maximum, 1.

    return stretched


def img_display(img, ax, bands, stretch_args=None, **imshow_args):
    '''
    This is where you should write a docstring.
    '''
    dispimg = img.copy().astype(np.float32)  # make a copy of the original image,
    # but be sure to cast it as a floating-point image, rather than an integer

    for b in range(img.shape[0]):  # loop over each band, stretching using percentile_stretch()
        if stretch_args is None:  # if stretch_args is None, use the default values for percentile_stretch
            dispimg[b] = percentile_stretch(img[b])
        else:
            dispimg[b] = percentile_stretch(img[b], **stretch_args)

    # next, we transpose the image to re-order the indices
    dispimg = dispimg.transpose([1, 2, 0])

    # finally, we display the image
    handle = ax.imshow(dispimg[:, :, bands], **imshow_args)

    return handle, ax


# ------------------------------------------------------------------------
# note - rasterio's open() function works in much the same way as python's - once we open a file,
# we have to make sure to close it. One easy way to do this in a script is by using the with statement shown
# below - once we get to the end of this statement, the file is closed.
with rio.open('data_files/NI_Mosaic.tif') as dataset:
    img = dataset.read()
    xmin, ymin, xmax, ymax = dataset.bounds

# your code goes here!
# start by loading the outlines and point data to add to the map
counties = gpd.read_file('../Week3/data_files/Counties.shp').to_crs('epsg:32629')
towns = gpd.read_file(r'C:\Users\charl\Documents\EGM722\egm722\Week2\data_files\Towns.shp')

# next, create the figure and axis objects to add the map to
myCRS = ccrs.UTM(29)
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# now, add the satellite image to the map
my_kwargs = {'extent': [xmin, xmax, ymin, ymax],
             'transform': myCRS}

h, ax = img_display(img, ax, [2, 1, 0], stretch_args={'pmin': 0.1, 'pmax': 99.9}, **my_kwargs)

# next, add the county outlines to the map
county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')
ax.add_feature(county_outlines)
def generate_handles(labels, colors, edge='k', alpha=1):
    '''
    This is where you should write a docstring.
    '''
    lc = len(colors)  # get the length of the color list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles
county_handles = generate_handles([''], ['none'], edge='r')

# then, add the town and city points to the map, but separately
town_points = towns['STATUS'] == 'Town'
city_points = towns['STATUS'] == 'City'
town_handle = ax.plot(towns[town_points].geometry.x, towns[town_points].geometry.y, 'D', color='#052AA7', ms=5, transform=myCRS)
city_handle = ax.plot(towns[city_points].geometry.x, towns[city_points].geometry.y, 'o', color='k', ms=10, transform=myCRS)

#add legend
ax.legend(county_handles + town_handle + city_handle,
          ['County Boundaries', 'Town', 'City'], fontsize=12, loc='upper left', framealpha=1)

# finally, try to add a transparent overlay to the map
# note: one way you could do this is to combine the individual county shapes into a single shape, then
# use a geometric operation, such as a symmetric difference, to create a hole in a rectangle.
# then, you can add the output of the symmetric difference operation to the map as a semi-transparent feature.
border = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])
union = counties.unary_union
overlay = ShapelyFeature(border.symmetric_difference(union), myCRS, facecolor='w', alpha=0.3)
ax.add_feature(overlay)
# last but not least, add gridlines to the map
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# and of course, save the map!
fig.savefig('imgs/exercise_map.png', dpi=300, bbox_inches='tight')
