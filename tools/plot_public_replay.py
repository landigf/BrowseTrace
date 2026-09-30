#!/usr/bin/env python3
"""Render the committed public replay at 5 MiB, with request and byte hit ratios."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'reports/public-cache-replay.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,2,figsize=(12,4.5))
colors={'LRU':'#8e969e','GDSF':'#9b252d'}
for ax,key,title in zip(axes,['request_hit_ratio','byte_hit_ratio'],['Request hit rate (%)','Byte hit rate (%)']):
 for j,policy in enumerate(['LRU','GDSF']):
  vals=[next(r[key]*100 for r in data['results'] if r['workload']==w and r['policy']==policy and r['cache_mib']==5) for w in ['scripted','llm']]
  bars=ax.bar([i+(j-.5)*.31 for i in range(2)],vals,.29,label=policy,color=colors[policy])
  ax.bar_label(bars,labels=[f'{v:.1f}%' for v in vals],padding=5,fontweight='bold',color=colors[policy])
 ax.set_xticks([0,1],['Scripted control','LLM-labelled trace']);ax.set_ylim(0,100);ax.set_title(title,loc='left',fontweight='bold',pad=18);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.5,.025))
fig.suptitle('BrowseTrace · offline replay at 5 MiB',x=.075,ha='left',fontsize=16,fontweight='bold')
fig.subplots_adjust(top=.8,bottom=.22,wspace=.25)
for suffix in ['svg','png','pdf']:
 fig.savefig(ROOT/f'assets/cache-replay.{suffix}',dpi=180,bbox_inches='tight',metadata={'Creator':'BrowseTrace plot_public_replay.py'})

svg = ROOT / 'assets/cache-replay.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
