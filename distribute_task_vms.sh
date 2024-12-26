#!/bin/bash

# 定義 VM 名稱和可用區域
declare -A VM_LIST
VM_LIST["instance-20241215-071419"]="us-central1-a"
VM_LIST["instance-20241215-071520"]="northamerica-northeast1-c"
VM_LIST["instance-20241215-071631"]="europe-west1-d"
VM_LIST["instance-20241215-214321"]="northamerica-northeast2-c"
VM_LIST["instance-20241215-214421"]="us-west1-a"
VM_LIST["instance-20241215-214438"]="europe-west3-c"
VM_LIST["instance-20241215-214502"]="europe-west9-c"

# 定義數字範圍
START=4900
END=11290
TOTAL_VMS=${#VM_LIST[@]}

# 每台 VM 處理的數字範圍
RANGE=$(( (END - START + 1) / TOTAL_VMS ))

# 取得所有 VM 名稱的順序
VM_NAMES=("${!VM_LIST[@]}")

# 迴圈分配範圍給每台 VM
CURRENT_START=$START

for VM in "${VM_NAMES[@]}"; do
    ZONE=${VM_LIST[$VM]}
    CURRENT_END=$(( CURRENT_START + RANGE - 1 ))

    # 如果是最後一台 VM，確保範圍到 END
    if [[ $VM == "${VM_NAMES[-1]}" ]]; then
        CURRENT_END=$END
    fi

    echo "🚀 分配範圍 $CURRENT_START 到 $CURRENT_END 給 VM: $VM 位於區域: $ZONE"

    # Python 腳本內容
    PYTHON_SCRIPT=$(cat <<EOF
print(f"Processing range: {list(range($CURRENT_START, $CURRENT_END + 1))}")
EOF
)

    # 在目標 VM 上創建並執行 Python 腳本
    gcloud compute ssh "$VM" --zone="$ZONE" --command="echo '$PYTHON_SCRIPT' > /tmp/task.py && python3 /tmp/task.py"

    echo "✅ 完成 VM: $VM"

    # 更新起始數字
    CURRENT_START=$(( CURRENT_END + 1 ))
done
