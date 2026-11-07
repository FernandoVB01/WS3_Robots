import json,subprocess,time,os,signal
from pathlib import Path
base=Path('/ws/evidencias'); video=base/'videos/03_office_0_supervisado.mp4'; log=base/'logs/office_0_r3_exploracion.jsonl'
while not video.exists():time.sleep(2)
previous=0
while True:
 time.sleep(180)
 stamp=time.strftime('%Y%m%d_%H%M%S');size=video.stat().st_size
 events=[]
 if log.exists():
  for line in log.read_text().splitlines():
   try:events.append(json.loads(line))
   except ValueError:pass
 maps=[e for e in events if e.get('event')=='map_evaluated']
 state={'time':stamp,'video_bytes':size,'video_growing':size>previous,'last_event':events[-1] if events else None,'review':'automatic_checks_and_screenshot_not_visual_approval'}
 previous=size
 out=base/'diagnostico'/('revision_3min_'+stamp+'.png')
 result=subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-f','x11grab','-video_size','1280x720','-i',':1.0','-frames:v','1','-update','1','-y',str(out)],timeout=30)
 state['screenshot_exit']=result.returncode
 if maps and (maps[-1]['width']*maps[-1]['resolution']>13 or maps[-1]['height']*maps[-1]['resolution']>12):
  state['alert']='Map exceeds expected office_0 bounds: stop to inspect possible SLAM drift'
  pid=int(Path('/home/ws3/run/explorador.pid').read_text())
  if b'explorar_fronteras.py' in Path(f'/proc/{pid}/cmdline').read_bytes():os.kill(pid,signal.SIGINT)
 print(json.dumps(state),flush=True)
 if 'alert' in state or (base/'logs/office_0_r3_cierre_autonomo.json').exists():break
