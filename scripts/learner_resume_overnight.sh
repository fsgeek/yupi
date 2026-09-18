#!/bin/bash
# After a reboot (or any interruption): put the overnight machinery back. Idempotent — safe to run
# even if parts are still alive (it checks). Everything it starts is resumable from disk.
set -u
L=/home/tony/.cache/yupi-scratch/runs/gpu
cd /home/tony/projects/hamutay
echo "lease status: $(./deploy/ayllu-gpu status 2>/dev/null | grep '"state"')"
if grep -q "SWEEP2M DONE" $L/sweep2M_2026-09-18.log 2>/dev/null; then
  echo "sweep already done"
  if ! pgrep -f size_2026-09-18.sh >/dev/null && ! grep -q "d256 seed 3 exit" $L/size_2026-09-18.log 2>/dev/null; then
    nohup ./deploy/ayllu-gpu run --holder yupi --purpose "yupi learner size axis at 2M windows (resumed)" --ttl 6h -- $L/size_2026-09-18.sh >> $L/size_2026-09-18.log 2>&1 &
    echo "size axis launched PID $!"
  fi
else
  if pgrep -f sweep2M_2026-09-18.sh >/dev/null; then echo "sweep still running"; else
    nohup ./deploy/ayllu-gpu run --holder yupi --purpose "yupi learner sweep at 2M windows (resumed after interruption)" --ttl 6h -- $L/sweep2M_2026-09-18.sh >> $L/sweep2M_2026-09-18.log 2>&1 &
    pid=$!; echo "sweep relaunched PID $pid"
    if ! pgrep -f babysit_2026-09-18.sh >/dev/null; then
      nohup $L/babysit_2026-09-18.sh $pid >> $L/babysit_2026-09-18.log 2>&1 & echo "babysitter relaunched PID $!"
    fi
  fi
fi
if pgrep -f eval_loop_2M_2026-09-18.sh >/dev/null; then echo "eval loop still running"; else
  nohup /home/tony/.cache/yupi-scratch/runs/eval_loop_2M_2026-09-18.sh >> /home/tony/.cache/yupi-scratch/runs/eval_loop_2M_2026-09-18.log 2>&1 & echo "eval loop relaunched PID $!"
fi
