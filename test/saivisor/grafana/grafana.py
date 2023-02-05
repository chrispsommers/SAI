from string import Template
from .grafana_templates import *

import logging
logger = logging.getLogger('grafana module')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
log_format = '[%(asctime)-15s] [%(levelname)08s] %(module)s.%(funcName)s-%(lineno)d: %(message)s'
logging.basicConfig(format=log_format)

def emit_dashboard_header():
  logger.info("Generating Grafana dashboard header...")
  return grafana_dash_template_hdr.substitute({})

def emit_dashboard_footer(title="SAI Visor", dash_uid="0"):
  logger.info("Generating Grafana dashboard footer...")
  return grafana_dash_template_footer.substitute({'title':title, 'dash_uid':dash_uid})

def emit_dashboard_panels(datasource_uid='0',
                         colorScheme='interpolateSpectral',
                         metrics=[]
                        ):
  panels = ''
  pnl_set_count=0 # might be 2-3 pnls per set

  pnl_height=8
  pnl_width=8
  pnl_num = 0

  # Lay out panels side-by-side for counters, heat map, delta heatmap
  def generate_panel_set(metric, datasource_uid,
    pnl_height,pnl_width,pnl_set_y,pnl_num, colorScheme):
      logger.info("  Generating Grafana panels for %s" % (metric))

      return grafana_dash_template_panel_api_latency.substitute(
        {
        'metric':metric,
        'datasource_uid':datasource_uid,
        # three panels per row, lay them out in a grid
        'grid_h':"%d" % pnl_height,
        'grid_w':"%d" % pnl_width,
        # x position side-by-side
        'grid_x0':"%d" % 0,'grid_x1':"%d" %pnl_width,'grid_x2':"%d" % pnl_width*2,
        # same vertical pos for all three pnls
        'grid_y0':"%d" % pnl_set_y,'grid_y1':"%d" % pnl_set_y,'grid_y2':"%d" % pnl_set_y,
        # unique panel IDs
        'pnl_id0': pnl_num,'pnl_id1': pnl_num+1,'pnl_id2': pnl_num+2,
        'colorScheme':colorScheme
        })


  logger.info("Generating Grafana dashboard panels...")
  for metric in metrics:
    if pnl_set_count > 0:
      panels += ',\n'
    pnl_set_y = pnl_set_count*pnl_height
    pnl_set_count+=1
    pnl_num +=3
    panels += generate_panel_set(
      metric,
      datasource_uid,
      pnl_height,pnl_width,pnl_set_y,pnl_num,colorScheme)

  logger.info("Generated %d panels total" % pnl_num)
  return panels

def emit_dashboard_config(title='SAI Visor',
    dash_uid='0', datasource_uid='0',
    colorScheme='interpolateSpectral',
    metrics=[]):
  return emit_dashboard_header() + \
    emit_dashboard_panels(
        datasource_uid=datasource_uid,
        colorScheme=colorScheme,
        metrics=metrics
    ) + \
    emit_dashboard_footer(title=title, dash_uid=dash_uid)