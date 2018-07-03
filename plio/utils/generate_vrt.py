import gdal
import os
import jinja2
import numpy as np

from plio.spatial.footprint import generate_gcps

def warped_vrt(camera, raster_size, fpath, outpath=None, no_data_value=0):
    gcps = generate_gcps(camera)
    xsize, ysize = raster_size

    if outpath is None:
        outpath = os.path.dirname(fpath)
    outname = os.path.splitext(os.path.basename(fpath))[0] + '.vrt'
    outname = os.path.join(outpath, outname)

    xsize, ysize = raster_size
    vrt = r'''<VRTDataset rasterXSize="{{ xsize }}" rasterYSize="{{ ysize }}">
     <Metadata/>
     <GCPList Projection="{{ proj }}">
     {% for gcp in gcps -%}
       {{gcp}}
     {% endfor -%}
    </GCPList>
     <VRTRasterBand dataType="Float32" band="1">
       <NoDataValue>{{ no_data_value }}</NoDataValue>
       <Metadata/>
       <ColorInterp>Gray</ColorInterp>
       <SimpleSource>
         <SourceFilename relativeToVRT="0">{{ fpath }}</SourceFilename>
         <SourceBand>1</SourceBand>
         <SourceProperties rasterXSize="{{ xsize }}" rasterYSize="{{ ysize }}"
    DataType="Float32" BlockXSize="512" BlockYSize="512"/>
         <SrcRect xOff="0" yOff="0" xSize="{{ xsize }}" ySize="{{ ysize }}"/>
         <DstRect xOff="0" yOff="0" xSize="{{ xsize }}" ySize="{{ ysize }}"/>
       </SimpleSource>
     </VRTRasterBand>
    </VRTDataset>'''

    context = {'xsize':xsize, 'ysize':ysize,
               'gcps':gcps,
               'proj':'+proj=longlat +a=3396190 +b=3376200 +no_defs',
               'fpath':fpath,
               'no_data_value':no_data_value}
    template = jinja2.Template(vrt)
    tmp = template.render(context)
    warp_options = gdal.WarpOptions(format='VRT', dstNodata=0)
    gdal.Warp(outname, tmp, options=warp_options)
