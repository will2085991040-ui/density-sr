const {execSync}=require('child_process');
const out=execSync('powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -match \"python|dsr_sr|node|pyinstaller|pyinstaller\" } | Select-Object ProcessId,Name,@{n=\'Cmd\';e={$_.CommandLine}} | ConvertTo-Json -Compress"',{encoding:'utf8',maxBuffer:50*1024*1024});
console.log(String(out).slice(0,2000));
