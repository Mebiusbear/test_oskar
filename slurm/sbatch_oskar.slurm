#!/bin/bash

#! 作业名称
#SBATCH --job-name Oskar_with_tec
#! 计费账号
#SBATCH --account astro
#! 需要的节点数
#SBATCH --nodes=1
#! 总任务数
#SBATCH --ntasks=1
#! 内存限制
##SBATCH --mem 100000M
#! 时间限制
#SBATCH --time=00:00:00
#! 邮箱
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=liuyihong@cnlab.net
#! 不重新排队
##SBATCH --no-requeue
#! 指定分区
#SBATCH --partition astro-cpu
#! 集群名称
#SBATCH --clusters astrolab
#! 最大switches数
#SBATCH --switches=1
#! 优先使用那个node
#SBATCH --nodelist astrolab-hpc-[2]
#! 避开哪个node
##SBATCH --exclude astrolab-hpc-[1]
#! 输出文件名
#SBATCH --output ./slurm/slurm_out/slurm-sim-%A.out
#! 是否独占节点
##SBATCH --exclusive
#SBATCH --cpus-per-task=32

source /home/liuyihong/.bashrc

# conda activate iono_proj

#! Set up python
echo -e "[main]Running python: `which python`"
echo -e "[main]which main in node: `hostname`"
echo -e "[main]Running dask-scheduler: `which dask-scheduler`"

cd $SLURM_SUBMIT_DIR
echo -e "[main]Changed directory to `pwd`\n"

JOBID=${SLURM_JOB_ID}
echo ${SLURM_JOB_NODELIST}

#! 把调度器跑起来
localdir=/tmp/liuyihong
mkdir -p ${localdir}
protool=tcp
scheduler=10.10.20.202
port=28886
dashboardport=28885
dask-scheduler --dashboard-address $dashboardport --protocol ${protool} --interface ib0 --port $port &
echo dask-scheduler started on ${scheduler}:${port}
sleep 2


#! 把worker跑起来 输出worker status
srun -o ./slurm/slurm_out/slurm_worker/srun_%x_%j_worker_%n.out dask-worker --nprocs 32 --nthreads 1 --interface ib0 --memory-limit 460GiB --local-directory ${localdir} ${protool}://${scheduler}:${port} &
echo dask-worker started on all nodes


sleep 1
echo "[main]Scheduler and workers now running"


#! We need to tell dask Client (inside python) where the scheduler is running
echo "Scheduler is running at ${scheduler}"

cd run_dir
rm -r *fits *vis *ms *log 

# OSKAR-2.8.3-dev-93a9459-Python3.sif
# OSKAR-A100-python3-cuda11_2.sif
singularity run --nv -H $PWD ../OSKAR-A100-python3-cuda11_2.sif python3 src/main.py

