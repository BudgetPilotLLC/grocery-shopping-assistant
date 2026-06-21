param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8787
)

python -m app.server --host $HostName --port $Port

