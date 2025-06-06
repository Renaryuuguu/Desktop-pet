# 图片批量重命名脚本
# 将指定文件夹内的图片按 _000_125, _001_125, _002_125 等格式重命名

# 设置文件夹路径
$folderPath = "C:\Users\tinmo\Desktop-pet\assets\pet\image\dragging"

# 获取文件夹中的所有图片文件
$files = Get-ChildItem -Path $folderPath -File | 
         Where-Object { $_.Extension -match '\.(jpg|jpeg|png|gif|bmp)' } |
         Sort-Object Name

# 计数器从0开始
$counter = 0

# 遍历所有图片文件
foreach ($file in $files) {
    # 生成新文件名，格式为 _000_125 等
    $newName = "_" + ("{0:D3}" -f $counter) + "_125" + $file.Extension
    
    # 构建完整的新文件路径
    $newPath = Join-Path -Path $folderPath -ChildPath $newName
    
    # 重命名文件
    Rename-Item -Path $file.FullName -NewName $newName
    
    # 输出重命名信息
    Write-Host "Renamed: $($file.Name) -> $newName"
    
    # 计数器加1
    $counter++
}

Write-Host "`nAll files renamed successfully! Total processed: $counter files."