#!/usr/bin/env python3
"""Finalize this run's map/video after its explorer exits, independently of chat."""
import argparse,json,os,signal,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('world');p.add_argument('map_name');p.add_argument('video');a=p.parse_args()
run=Path('/home/ws3/run'); log=Path('/ws/evidencias/logs')
explorer=int((run/'explorador.pid').read_text()); recorder=int((run/'record.pid').read_text())
def identity(pid):
 try:
  stat=Path(f'/proc/{pid}/stat').read_text().split()
  return stat[21] if stat[2]!='Z' else None
 except OSError:return None
explorer_id=identity(explorer); recorder_id=identity(recorder)
assert explorer_id and recorder_id,'Missing active explorer or recorder'
def event(name,**kw):print(json.dumps({'event':name,'unix_time':time.time(),**kw}),flush=True)
event('watching',explorer_pid=explorer,recorder_pid=recorder,world=a.world)
while identity(explorer)==explorer_id:time.sleep(5)
event('explorer_exited');time.sleep(20)
with (log/(a.world+'_guardado_autonomo.log')).open('w') as f:
 try:
  saved=subprocess.run(['ros2','run','nav2_map_server','map_saver_cli','-f','/ws/evidencias/mapas/'+a.map_name,'--ros-args','-r','map:=/do100_0000/map','-p','use_sim_time:=true','-p','save_map_timeout:=20.0'],stdout=f,stderr=subprocess.STDOUT,timeout=45).returncode
 except subprocess.TimeoutExpired:saved=124
try:
 subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-f','x11grab','-video_size','1280x720','-i',':1.0','-frames:v','1','-update','1','-y','/ws/evidencias/mapas/'+a.world+'_pantalla_final.png'],timeout=20,check=False)
except subprocess.TimeoutExpired:event('screenshot_timeout')
if identity(recorder)==recorder_id:
 os.kill(recorder,signal.SIGINT)
 for _ in range(30):
  if identity(recorder)!=recorder_id:break
  time.sleep(1)
probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',a.video],capture_output=True,text=True,timeout=20)
status={'world':a.world,'map_save_exit':saved,'ffprobe_exit':probe.returncode,'video':a.video,'completed_unix_time':time.time(),'coverage_review_required':True}
if probe.returncode==0:status['media']=json.loads(probe.stdout)
(log/(a.world+'_cierre_autonomo.json')).write_text(json.dumps(status,indent=2)+'\n')
event('finalized',**status)
