#!/usr/bin/env python3
"""Normaliza os controladores de interface do visor V2.2.1."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs/assets/js/pih.js"


def replace_line(text: str, prefix: str, replacement: str) -> str:
    lines = text.splitlines()
    matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Esperada uma linha com {prefix!r}, encontradas {len(matches)}")
    lines[matches[0]] = replacement.strip()
    return "\n".join(lines) + "\n"


text = TARGET.read_text(encoding="utf-8")
text = replace_line(
    text,
    "map.on('click',e=>{if(activeIRKey)",
    "map.on('click',event=>{if(openActiveCellAt(event.latlng))return;if(wellSelectMode)openNearestWell(event.latlng);});map.on('mousemove',event=>{if(!wellSelectMode)return;clearTimeout(hoverWellTimer);hoverWellTimer=setTimeout(()=>{const hit=nearestActiveWell(event.latlng,22);setMapCursor(hit?'pointer':'crosshair');},45);});",
)
text = replace_line(
    text,
    "document.querySelectorAll('[data-layer]').forEach",
    "document.querySelectorAll('[data-layer]').forEach(input=>input.addEventListener('change',()=>{toggle(input.dataset.layer,input.checked);updateActiveLayerCount();}));document.getElementById('navLayers').onclick=()=>{app.classList.toggle('left-closed');setTimeout(()=>map.invalidateSize(),220);};document.getElementById('navEvidence').onclick=()=>focusLayerGroup('evidenceGroup');document.getElementById('closeLayers').onclick=()=>{app.classList.add('left-closed');setTimeout(()=>map.invalidateSize(),220);};document.getElementById('closeFicha').onclick=closeRight;document.getElementById('fitState').onclick=async()=>map.fitBounds((await ensureLayer('boundary')).getBounds(),{padding:[10,10]});document.getElementById('zoomIn').onclick=()=>map.zoomIn();document.getElementById('zoomOut').onclick=()=>map.zoomOut();document.getElementById('locateMe').onclick=locateUser;document.getElementById('clearOptional').onclick=clearOptionalLayers;document.getElementById('baseMapButton').onclick=()=>{const menu=document.getElementById('basemapMenu'),button=document.getElementById('baseMapButton');menu.hidden=!menu.hidden;button.setAttribute('aria-expanded',String(!menu.hidden));};document.getElementById('closeBasemap').onclick=()=>{document.getElementById('basemapMenu').hidden=true;document.getElementById('baseMapButton').setAttribute('aria-expanded','false');};document.querySelectorAll('input[name=basemap]').forEach(input=>input.addEventListener('change',()=>setBase(input.value)));document.getElementById('navMap').onclick=()=>{closeRight();setTimeout(()=>map.invalidateSize(),180);};setupNavMenus();setupModals();setupLayerToolbar();setupHelpSearch();",
)
text = replace_line(
    text,
    "const spatialShow=document.getElementById('showSpatialStructure')",
    "const spatialShow=document.getElementById('showSpatialStructure'),spatialHide=document.getElementById('hideSpatialStructure'),spatialMetricEl=document.getElementById('spatialMetric'),spatialEvidenceEl=document.getElementById('spatialEvidence'),spatialScaleEl=document.getElementById('spatialScale');if(spatialShow)spatialShow.onclick=showSpatialStructure;if(spatialHide)spatialHide.onclick=hideSpatialStructure;if(spatialMetricEl)spatialMetricEl.onchange=()=>{updateSpatialEvidenceControl();if(activeSpatialKey)showSpatialStructure()};if(spatialEvidenceEl)spatialEvidenceEl.onchange=()=>{if(activeSpatialKey)showSpatialStructure()};if(spatialScaleEl)spatialScaleEl.onchange=()=>{if(activeSpatialKey)showSpatialStructure()};const navSpatial=document.getElementById('navSpatialStructure');if(navSpatial)navSpatial.onclick=()=>{focusLayerGroup('spatialStructureGroup');updateSpatialEvidenceControl();};updateSpatialEvidenceControl();",
)
text = replace_line(
    text,
    "const stratShow=document.getElementById('showStratified')",
    "const stratShow=document.getElementById('showStratified'),stratHide=document.getElementById('hideStratified'),stratMetric=document.getElementById('stratMetric'),stratScale=document.getElementById('stratScale');if(stratShow)stratShow.onclick=showStratified;if(stratHide)stratHide.onclick=hideStratified;if(stratMetric)stratMetric.onchange=()=>{if(activeStratifiedKey)showStratified()};if(stratScale)stratScale.onchange=()=>{if(activeStratifiedKey)showStratified()};const navStrat=document.getElementById('navStratified');if(navStrat)navStrat.onclick=()=>focusLayerGroup('stratifiedGroup');",
)
text = replace_line(
    text,
    "const scaleStudyShow=document.getElementById('showScaleStudy')",
    "const scaleStudyShow=document.getElementById('showScaleStudy'),scaleStudyHide=document.getElementById('hideScaleStudy'),scaleStudyMetric=document.getElementById('scaleStudyMetric'),scaleStudyScale=document.getElementById('scaleStudyScale');if(scaleStudyShow)scaleStudyShow.onclick=showScaleStudy;if(scaleStudyHide)scaleStudyHide.onclick=hideScaleStudy;if(scaleStudyMetric)scaleStudyMetric.onchange=()=>{if(activeScaleStudyKey)showScaleStudy()};if(scaleStudyScale)scaleStudyScale.onchange=()=>{if(activeScaleStudyKey)showScaleStudy()};const navScaleStudy=document.getElementById('navScaleStudy');if(navScaleStudy)navScaleStudy.onclick=()=>focusLayerGroup('scaleStudyGroup');",
)
text = replace_line(
    text,
    "const ekShow=document.getElementById('showEffectiveKnowledge')",
    "const ekShow=document.getElementById('showEffectiveKnowledge'),ekHide=document.getElementById('hideEffectiveKnowledge'),ekMetricEl=document.getElementById('ekMetric'),ekScaleEl=document.getElementById('ekScale');if(ekShow)ekShow.onclick=showEffectiveKnowledge;if(ekHide)ekHide.onclick=hideEffectiveKnowledge;if(ekMetricEl)ekMetricEl.onchange=()=>{if(activeEKKey)showEffectiveKnowledge()};if(ekScaleEl)ekScaleEl.onchange=()=>{if(activeEKKey)showEffectiveKnowledge()};const navEK=document.getElementById('navEffectiveKnowledge');if(navEK)navEK.onclick=()=>focusLayerGroup('effectiveKnowledgeGroup');",
)
text = replace_line(
    text,
    "const irShow=document.getElementById('showIndependence')",
    "const irShow=document.getElementById('showIndependence'),irHide=document.getElementById('hideIndependence'),irMetricEl=document.getElementById('irMetric'),irScaleEl=document.getElementById('irScale');if(irShow)irShow.onclick=showIndependence;if(irHide)irHide.onclick=hideIndependence;if(irMetricEl)irMetricEl.onchange=()=>{if(activeIRKey)showIndependence()};if(irScaleEl)irScaleEl.onchange=()=>{if(activeIRKey)showIndependence()};const navIR=document.getElementById('navIndependence');if(navIR)navIR.onclick=()=>focusLayerGroup('independenceGroup');",
)
text = replace_line(
    text,
    "const vtShow=document.getElementById('showVerticalTemporal')",
    "const vtShow=document.getElementById('showVerticalTemporal'),vtHide=document.getElementById('hideVerticalTemporal'),vtMetricEl=document.getElementById('vtMetric'),vtScaleEl=document.getElementById('vtScale');if(vtShow)vtShow.onclick=showVerticalTemporal;if(vtHide)vtHide.onclick=hideVerticalTemporal;if(vtMetricEl)vtMetricEl.onchange=()=>{if(activeVTKey)showVerticalTemporal()};if(vtScaleEl)vtScaleEl.onchange=()=>{if(activeVTKey)showVerticalTemporal()};const navVT=document.getElementById('navVerticalTemporal');if(navVT)navVT.onclick=()=>focusLayerGroup('verticalTemporalGroup');",
)
text = replace_line(
    text,
    "const gridShow=document.getElementById('showGridEvidence')",
    "const gridShow=document.getElementById('showGridEvidence'),gridHide=document.getElementById('hideGridEvidence'),gridCode=document.getElementById('gridEvidenceCode');if(gridShow)gridShow.onclick=showGridEvidence;if(gridHide)gridHide.onclick=hideGridEvidence;if(gridCode)gridCode.onchange=()=>{if(activeGridEvidenceKey)showGridEvidence()};const gridScale=document.getElementById('gridEvidenceScale');if(gridScale)gridScale.onchange=()=>{if(activeGridEvidenceKey)showGridEvidence()};const navGrid=document.getElementById('navGridEvidence');if(navGrid)navGrid.onclick=()=>focusLayerGroup('gridEvidenceGroup');",
)
TARGET.write_text(text, encoding="utf-8")
print("OK controladores V2.2.1")
