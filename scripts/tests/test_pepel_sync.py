import os, subprocess, tempfile, unittest
from pathlib import Path
SCRIPT=(Path(__file__).resolve().parents[1] / 'pepel-sync')
NAMES=('reservation','reservation-gas','pepelmoco-site')
class SyncTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='pepel-sync-test-');self.base=Path(self.tmp.name)
  self.home=self.base/'home';self.home.mkdir();self.roots=self.home/'different layout';self.roots.mkdir()
  self.env=dict(os.environ,HOME=str(self.home),GIT_CONFIG_GLOBAL=str(self.base/'gitconfig'),GIT_CONFIG_NOSYSTEM='1',GIT_AUTHOR_NAME='Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
  self.paths={};self.bares={};self.writers={}
  for i,n in enumerate(NAMES):
   bare=self.base/(n+'.git');self.git(None,'init','--bare','--initial-branch=main',str(bare))
   writer=self.base/('writer-'+n);self.git(None,'clone',str(bare),str(writer));(writer/'content').write_text('base')
   self.git(writer,'add','content');self.git(writer,'commit','-m','fixture base');self.git(writer,'push','origin','main')
   local=self.roots/('arbitrary '+str(i));self.git(None,'clone',str(bare),str(local))
   url='https://github.com/pepelmocohair/'+n+'.git';self.git(local,'remote','set-url','origin',url)
   self.git(None,'config','--global','url.'+str(bare)+'.insteadOf',url)
   # get-url expands insteadOf; identity must use configured URLs rather than rewritten transports.
   self.paths[n]=local;self.bares[n]=bare;self.writers[n]=writer
 def tearDown(self): self.tmp.cleanup()
 def git(self,p,*args):
  cmd=['git']+(['-C',str(p)] if p else [])+list(args)
  r=subprocess.run(cmd,env=self.env,text=True,capture_output=True)
  if r.returncode: raise AssertionError((cmd,r.stderr))
  return r.stdout.strip()
 def run_sync(self,*args,explicit=False):
  opts=[]
  if explicit:
   for n,p in self.paths.items():opts+=['--repo',n+'='+str(p)]
  else:opts=['--root',str(self.roots)]
  return subprocess.run([str(SCRIPT),*opts,*args],env=self.env,text=True,capture_output=True)
 def head(self,n):return self.git(self.paths[n],'rev-parse','HEAD')
 def commit_local(self,n):
  p=self.paths[n];(p/'local').write_text('local');self.git(p,'add','local');self.git(p,'commit','-m','fixture local')
 def remote_advance(self,n):
  p=self.writers[n];(p/'remote').write_text('remote');self.git(p,'add','remote');self.git(p,'commit','-m','fixture remote');self.git(p,'push','origin','main')
 def stopped(self,mutate,explicit=False):
  # A safe behind repo must remain untouched when any peer fails.
  self.remote_advance('pepelmoco-site');mutate();before={n:self.head(n) for n in NAMES if self.paths[n].exists()}
  r=self.run_sync(explicit=explicit);self.assertNotEqual(r.returncode,0,r.stdout+r.stderr);self.assertIn('STOP',r.stdout)
  for n,h in before.items():self.assertEqual(self.head(n),h)
  return r
 def test_unrelated_invalid_git_marker(self):
  junk=self.roots/'codex placeholder';junk.mkdir();(junk/'.git').mkdir()
  # Target clone inside the invalid placeholder must still be found.
  self.paths['reservation'].rename(junk/'nested repo');self.paths['reservation']=junk/'nested repo'
  r=self.run_sync();self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertIn('WARN:',r.stdout)
 def test_repeat_sync_after_fast_forward(self):
  for n in ['reservation','reservation-gas']:self.remote_advance(n)
  before={n:self.head(n) for n in NAMES}
  check=self.run_sync('--check');self.assertEqual(check.returncode,0,check.stdout+check.stderr)
  for n in ['reservation','reservation-gas']:
   self.assertIn(n+': fetch=OK ahead=0 behind=1 diverged=no',check.stdout)
   self.assertEqual(self.head(n),before[n])
  first=self.run_sync();self.assertEqual(first.returncode,0,first.stdout+first.stderr)
  for n in ['reservation','reservation-gas']:
   self.assertIn('UPDATED '+n+':',first.stdout)
   self.assertEqual(self.head(n),self.git(self.paths[n],'rev-parse','refs/remotes/origin/main'))
   self.assertNotEqual(self.head(n),before[n])
  updated={n:self.head(n) for n in NAMES}
  for args in [(),(),('--check',)]:
   again=self.run_sync(*args);self.assertEqual(again.returncode,0,again.stdout+again.stderr)
   self.assertNotIn('UPDATED',again.stdout)
   for n in NAMES:
    self.assertIn(n+': fetch=OK ahead=0 behind=0 diverged=no',again.stdout)
    self.assertIn('OK      '+n+':',again.stdout)
    self.assertEqual(self.head(n),updated[n])
    self.assertEqual(self.git(self.paths[n],'status','--porcelain'),'')
 def test_clean(self):
  r=self.run_sync();self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertEqual(r.stdout.count('main一致・clean'),3)
 def test_dirty(self):self.stopped(lambda:(self.paths['reservation']/'untracked').write_text('dirty'))
 def test_ahead(self):self.assertIn('ahead（',self.stopped(lambda:self.commit_local('reservation')).stdout)
 def test_behind(self):
  before=self.head('reservation');self.remote_advance('reservation');r=self.run_sync();self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertIn('UPDATED',r.stdout);self.assertNotEqual(before,self.head('reservation'));self.assertEqual(self.git(self.paths['reservation'],'status','--porcelain'),'')
 def test_diverged(self):
  self.remote_advance('reservation');self.assertIn('diverged',self.stopped(lambda:self.commit_local('reservation')).stdout)
 def test_missing(self):
  r=self.stopped(lambda:self.paths['reservation'].rename(self.base/'outside-scan'));self.assertIn('reservation: 未発見',r.stdout)
 def test_wrong_origin(self):
  r=self.stopped(lambda:self.git(self.paths['reservation'],'remote','set-url','origin','https://github.com/other/reservation.git'),explicit=True);self.assertIn('想定外origin',r.stdout)
 def test_fetch_failure(self):
  # Keep logical origin intact but route it to an unavailable local bare repo.
  def change():
   url='https://github.com/pepelmocohair/reservation.git';self.git(None,'config','--global','--unset-all','url.'+str(self.bares['reservation'])+'.insteadOf');self.git(None,'config','--global','url.'+str(self.base/'missing.git')+'.insteadOf',url)
  self.assertIn('fetch/比較失敗',self.stopped(change).stdout)
 def test_detached(self):self.stopped(lambda:self.git(self.paths['reservation'],'checkout','--detach'))
 def test_other_branch(self):self.stopped(lambda:self.git(self.paths['reservation'],'checkout','-b','topic'))
 def test_duplicate_clone(self):
  extra=self.roots/'another copy';self.git(None,'clone',str(self.bares['reservation']),str(extra));self.git(extra,'remote','set-url','origin','https://github.com/pepelmocohair/reservation.git')
  r=self.run_sync();self.assertNotEqual(r.returncode,0);self.assertIn('複数コピー',r.stdout)
  r=self.run_sync(explicit=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_check_does_not_update(self):
  before=self.head('reservation');self.remote_advance('reservation');r=self.run_sync('--check');self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertEqual(self.head('reservation'),before)
 def test_worktree(self):
  n='reservation';old=self.paths[n];p=self.roots/'linked worktree';self.git(old,'worktree','add','--detach',str(p));self.git(old,'checkout','--detach');self.git(p,'checkout','main');old.rename(self.base/'old-checkout')
  # Moving parent breaks worktree metadata; use the original checkout outside scan instead.
  self.git(self.base/'old-checkout','worktree','repair',str(p));self.paths[n]=p
  r=self.run_sync();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_update_failure(self):
  self.remote_advance('reservation');before={n:self.head(n) for n in NAMES}
  import shutil
  real=shutil.which('git');bin_dir=self.base/'bin';bin_dir.mkdir();wrapper=bin_dir/'git'
  wrapper.write_text('#!/bin/sh\nfor arg in "$@"; do if [ "$arg" = merge ]; then echo "fixture update failure" >&2; exit 23; fi; done\nexec '+real+' "$@"\n');wrapper.chmod(0o755)
  self.env['PATH']=str(bin_dir)+os.pathsep+self.env['PATH']
  r=self.run_sync();self.assertNotEqual(r.returncode,0);self.assertIn('更新/事後検査失敗',r.stdout)
  for n,h in before.items():self.assertEqual(self.head(n),h)
 def test_hooks_not_run(self):
  self.remote_advance('reservation');marker=self.base/'hook-ran';hook=self.paths['reservation']/'.git/hooks/post-merge';hook.write_text('#!/bin/sh\ntouch '+str(marker)+'\n');hook.chmod(0o755)
  r=self.run_sync();self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertFalse(marker.exists())
 def test_config(self):
  config=self.home/'.config/pepel-sync/repos.json';config.parent.mkdir(parents=True);import json;config.write_text(json.dumps({n:str(p) for n,p in self.paths.items()}))
  r=subprocess.run([str(SCRIPT)],env=self.env,text=True,capture_output=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
if __name__=='__main__':unittest.main(verbosity=2)
