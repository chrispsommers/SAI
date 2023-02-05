from string import Template

grafana_dash_template_hdr = Template("""{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "target": {
          "limit": 100,
          "matchAny": false,
          "tags": [],
          "type": "dashboard"
        },
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "liveNow": false,
  "panels": [
""")

grafana_dash_template_panel_api_latency = Template("""    {
      "cards": {},
      "color": {
        "cardColor": "#b4ff00",
        "colorScale": "sqrt",
        "colorScheme": "${colorScheme}",
        "exponent": 0.5,
        "mode": "spectrum"
      },
      "dataFormat": "tsbuckets",
      "gridPos": {
        "h": ${grid_h},
        "w": ${grid_w},
        "x": ${grid_x0},
        "y": ${grid_y0}
      },
      "heatmap": {},
      "hideZeroBuckets": false,
      "highlightCards": true,
      "id": ${pnl_id0},
      "legend": {
        "show": true
      },
      "reverseYBuckets": false,
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "${datasource_uid}"
          },
          "exemplar": true,
          "expr": "increase(${metric} {le!=\\"+Inf\\"} [15s])",
          "format": "heatmap",
          "interval": "",
          "legendFormat": "{{le}}",
          "refId": "A"
        }
      ],
      "title": "${metric} Heatmap 15s increases",
      "tooltip": {
        "show": true,
        "showHistogram": true
      },
      "type": "heatmap",
      "xAxis": {
        "show": true
      },
      "yAxis": {
        "format": "µs",
        "logBase": 1,
        "show": true
      },
      "yBucketBound": "auto"
    },
    {
      "cards": {},
      "color": {
        "cardColor": "#b4ff00",
        "colorScale": "sqrt",
        "colorScheme": "${colorScheme}",
        "exponent": 0.5,
        "mode": "spectrum"
      },
      "dataFormat": "tsbuckets",
      "gridPos": {
        "h": ${grid_h},
        "w": ${grid_w},
        "x": ${grid_x1},
        "y": ${grid_y1}
      },
      "heatmap": {},
      "hideZeroBuckets": false,
      "highlightCards": true,
      "id": ${pnl_id1},
      "legend": {
        "show": true
      },
      "reverseYBuckets": false,
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "${datasource_uid}"
          },
          "exemplar": true,
          "expr": "${metric} {le!=\\"+Inf\\"}",
          "format": "heatmap",
          "interval": "",
          "legendFormat": "{{le}}",
          "refId": "A"
        }
      ],
      "title": "${metric} Heatmap",
      "tooltip": {
        "show": true,
        "showHistogram": true
      },
      "type": "heatmap",
      "xAxis": {
        "show": true
      },
      "yAxis": {
        "format": "µs",
        "logBase": 1,
        "show": true
      },
      "yBucketBound": "auto"
    },
    {
      "description": "Cumulative # observations of latency measuring less than or equal to threshold",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "none"
        },
        "overrides": []
      },
      "gridPos": {
        "h": ${grid_h},
        "w": ${grid_w},
        "x": ${grid_x2},
        "y": ${grid_y2}
      },
      "id": ${pnl_id2},
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom"
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "${datasource_uid}"
          },
          "exemplar": true,
          "expr": "${metric} {le!=\\"+Inf\\"}",
          "interval": "",
          "legendFormat": "",
          "refId": "A"
        }
      ],
      "title": "${metric} counts",
      "type": "timeseries"
    }""")


grafana_dash_template_footer = Template("""
  ],
  "refresh": "5s",
  "schemaVersion": 35,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "${title}",
  "uid": "${dash_uid}",
  "version": 5,
  "weekStart": ""
}""")

