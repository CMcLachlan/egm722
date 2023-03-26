import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches


# ---------------------------------------------------------------------------------------------------------------------
# in this section, write the script to load the data and complete the main part of the analysis.
# try to print the results to the screen using the format method demonstrated in the workbook

# load the necessary data here and transform to a UTM projection
counties = gpd.read_file('data_files/Counties.shp')
wards = gpd.read_file('data_files/NI_Wards.shp')

myCRS = ccrs.UTM(29)

counties = counties.to_crs(myCRS) #transform crs to "myCRS"/UTM29
wards = wards.to_crs(myCRS)

# your analysis goes here...
wards['WARDAREA'] = wards['geometry'].area / 1e6  # calculate area of each ward
wards["Ward_ppsqkm"] = wards['Population']/wards['WARDAREA']  # calculate pop density of each ward

cwjoin = gpd.sjoin(counties, wards, how='inner', lsuffix='left', rsuffix='right') # perform the spatial join
# print(cwjoin.head()) #show joined data columns

print(cwjoin.groupby(['CountyName'])['Population'].sum()) #summarise ward population totals by county

wards_pop = wards['Population'].sum() #add up population from wards
joined_pop = cwjoin['Population'].sum() #add up population from spatial join

print('Total population sum from wards file: {:.2f}'.format(wards_pop)) #check if wards are overlapping county boundaries
print('Total population sum from spatial join: {:.2f}'.format(joined_pop))

print('Number of features in wards: {}'.format(len(wards.index)))
print('Number of features in joined: {}'.format(len(cwjoin.index)))  # check number of features in wards and joined data
print('Number of wards located in more than one county: {}'.format((len(cwjoin.index)-len(wards.index))/2))
print('Total population of wards located in more than one county: {}'.format((joined_pop-wards_pop)/2))
print('Highest ward population: {}'.format((wards['Population'].max())))
print('Ward with highest population: {}'.format(wards.loc[wards['Population'] == 9464, 'Ward']))

# ---------------------------------------------------------------------------------------------------------------------
# below here, you may need to modify the script somewhat to create your map.
# create a crs using ccrs.UTM() that corresponds to our CRS
myCRS = ccrs.UTM(29)
# create a figure of size 10x10 (representing the page size in inches
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

# plot the ward data into our axis, using
ward_plot = wards.plot(column='Ward_ppsqkm', ax=ax, vmin=300, vmax=10000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population density (people per square km)'})

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')

ax.add_feature(county_outlines)
county_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='r')]

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)

# save the figure
fig.savefig('population_density_map.png', dpi=300, bbox_inches='tight')
