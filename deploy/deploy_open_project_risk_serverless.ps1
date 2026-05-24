# OPEN Project Risk :: Deploy Yandex Serverless Container
# PowerShell 7+ script. Requires yc and docker.
# Real secrets should live in deploy/deploy_open_project_risk_serverless.local.ps1
# or environment variables. Do not commit local secret files.

$ErrorActionPreference = 'Stop'

# --------------------------- Config -----------------------------------------
$REGISTRY_ID = 'crpj9tkd4nn6hsiuodlm'
$REPO_NAME = 'open-project-risk-web'
$CONTAINER_NAME = 'open-project-risk-web'
$CONTAINER_ID = ''
$SERVICE_ACCOUNT_ID = 'ajeln24a03l3mcojsquh'
$YC_FOLDER_ID = ''

$APP_NAME = 'OPEN Project Risk'
$API_V1_PREFIX = '/api/v1'
$ENV = 'demo'
$DEBUG = 'false'

$DATABASE_URL = ''
$DEMO_AUTH_ENABLED = 'true'
$DEMO_AUTH_USERNAME = ''
$DEMO_AUTH_PASSWORD = ''
$SECRET_KEY = ''
$SESSION_COOKIE_NAME = 'open_project_risk_session'
$SESSION_TTL_SECONDS = '86400'

$MEMORY = '1G'
$CORES = 1
$CONCURRENCY = 4
$MIN_INSTANCES = 1
$EXECUTION_TIMEOUT = '60s'
$HEALTH_WAIT_SECONDS = 90

# Optional local overrides. This file is ignored by Git.
$LOCAL_CONFIG_PATH = Join-Path $PSScriptRoot 'deploy_open_project_risk_serverless.local.ps1'
if (Test-Path $LOCAL_CONFIG_PATH) {
  . $LOCAL_CONFIG_PATH
}

# --------------------------- Helpers ----------------------------------------
function Run-Proc {
  param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [string[]]$Args = @(),
    [int]$TimeoutSec = 600,
    [string]$WorkingDirectory = (Get-Location).Path
  )

  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $FilePath
  $psi.UseShellExecute = $false
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.WorkingDirectory = $WorkingDirectory
  foreach ($arg in $Args) {
    $psi.ArgumentList.Add($arg) | Out-Null
  }

  $process = New-Object System.Diagnostics.Process
  $process.StartInfo = $psi
  $null = $process.Start()
  if (-not $process.WaitForExit($TimeoutSec * 1000)) {
    try { $process.Kill($true) } catch { try { $process.Kill() } catch {} }
    throw "Timeout running $FilePath $($Args -join ' ')"
  }

  [pscustomobject]@{
    ExitCode = $process.ExitCode
    StdOut = $process.StandardOutput.ReadToEnd()
    StdErr = $process.StandardError.ReadToEnd()
  }
}

function Get-EnvOrValue {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$Value = ''
  )

  $envValue = (Get-Item "Env:$Name" -ErrorAction SilentlyContinue).Value
  if (-not [string]::IsNullOrWhiteSpace($envValue)) {
    return $envValue.Trim()
  }

  return ($Value ?? '').Trim()
}

function Validate-RequiredValue {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Value
  )

  if ([string]::IsNullOrWhiteSpace($Value)) {
    throw "$Name is empty. Fill it in deploy_open_project_risk_serverless.local.ps1 or set env:$Name before deploy."
  }
  if ($Value -match '<[^>]+>') {
    throw "$Name contains placeholder '$Value'. Replace it before deploy."
  }
}

function Validate-Tool {
  param([Parameter(Mandatory = $true)][string]$Name)

  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "$Name is not available in PATH."
  }
}

function Get-YcFolderId {
  param([string]$ConfiguredFolderId)

  if (-not [string]::IsNullOrWhiteSpace($ConfiguredFolderId)) {
    return $ConfiguredFolderId.Trim()
  }

  $folder = Run-Proc -FilePath 'yc' -Args @('config', 'get', 'folder-id') -TimeoutSec 30
  if ($folder.ExitCode -ne 0) {
    throw "YC_FOLDER_ID is empty and 'yc config get folder-id' failed. Fill YC_FOLDER_ID explicitly."
  }

  $value = $folder.StdOut.Trim()
  if ([string]::IsNullOrWhiteSpace($value)) {
    throw "YC_FOLDER_ID is empty and current yc config has no folder-id. Fill YC_FOLDER_ID explicitly."
  }

  return $value
}

function Get-ContainerIdByName {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$FolderId
  )

  $result = Run-Proc -FilePath 'yc' -Args @(
    'serverless', 'container', 'list',
    '--folder-id', $FolderId,
    '--format', 'json'
  ) -TimeoutSec 60

  if ($result.ExitCode -ne 0) {
    throw "Cannot list serverless containers: $($result.StdErr)"
  }

  $containers = @($result.StdOut | ConvertFrom-Json)
  $match = $containers | Where-Object { $_.name -eq $Name } | Select-Object -First 1
  if ($match) {
    return [string]$match.id
  }

  return ''
}

function Create-Container {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$FolderId
  )

  $result = Run-Proc -FilePath 'yc' -Args @(
    'serverless', 'container', 'create',
    '--name', $Name,
    '--folder-id', $FolderId,
    '--format', 'json'
  ) -TimeoutSec 90

  if ($result.ExitCode -ne 0) {
    throw "Cannot create serverless container '$Name': $($result.StdErr)"
  }

  $created = $result.StdOut | ConvertFrom-Json
  if (-not $created.id) {
    throw "Container '$Name' was created but id was not returned."
  }

  return [string]$created.id
}

function Resolve-ContainerId {
  param(
    [string]$ConfiguredContainerId,
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$FolderId
  )

  if (-not [string]::IsNullOrWhiteSpace($ConfiguredContainerId)) {
    Write-Host "Using configured container id: $ConfiguredContainerId"
    return $ConfiguredContainerId.Trim()
  }

  Write-Host "Looking for serverless container '$Name'..."
  $foundId = Get-ContainerIdByName -Name $Name -FolderId $FolderId
  if (-not [string]::IsNullOrWhiteSpace($foundId)) {
    Write-Host "Found container '$Name': $foundId"
    return $foundId
  }

  Write-Host "Container '$Name' was not found. Creating a new one..."
  $createdId = Create-Container -Name $Name -FolderId $FolderId
  Write-Host "Created container '$Name': $createdId"
  return $createdId
}

function Invoke-SmokeGet {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][int[]]$ExpectedStatuses,
    [int]$TimeoutSec = 20,
    [switch]$NoRedirect
  )

  try {
    if ($NoRedirect) {
      $handler = [System.Net.Http.HttpClientHandler]::new()
      $handler.AllowAutoRedirect = $false
      $client = [System.Net.Http.HttpClient]::new($handler)
      $client.Timeout = [TimeSpan]::FromSeconds($TimeoutSec)
      try {
        $response = $client.GetAsync($Url).GetAwaiter().GetResult()
        $statusCode = [int]$response.StatusCode
        if ($ExpectedStatuses -notcontains $statusCode) {
          throw "Unexpected status $statusCode for $Url. Expected: $($ExpectedStatuses -join ', ')"
        }

        $location = $response.Headers.Location
        if ($location) {
          Write-Host ("  OK    {0} {1} -> {2}" -f $statusCode, $Url, $location)
        }
        else {
          Write-Host ("  OK    {0} {1}" -f $statusCode, $Url)
        }
        return [pscustomobject]@{ StatusCode = $statusCode; Headers = @{ Location = [string]$location } }
      }
      finally {
        $client.Dispose()
        $handler.Dispose()
      }
    }

    $args = @{
      Method = 'GET'
      Uri = $Url
      UseBasicParsing = $true
      TimeoutSec = $TimeoutSec
      SkipHttpErrorCheck = $true
      ErrorAction = 'Stop'
    }
    $response = Invoke-WebRequest @args
    $statusCode = [int]$response.StatusCode
    if ($ExpectedStatuses -notcontains $statusCode) {
      throw "Unexpected status $statusCode for $Url. Expected: $($ExpectedStatuses -join ', ')"
    }

    $location = $response.Headers.Location
    if ($location) {
      Write-Host ("  OK    {0} {1} -> {2}" -f $statusCode, $Url, $location)
    }
    else {
      Write-Host ("  OK    {0} {1}" -f $statusCode, $Url)
    }
    return $response
  }
  catch {
    throw "Smoke check failed for $Url. $($_.Exception.Message)"
  }
}

function Wait-Health {
  param(
    [Parameter(Mandatory = $true)][string]$BaseUrl,
    [int]$Seconds = 90
  )

  $url = "$BaseUrl$API_V1_PREFIX/health"
  $deadline = (Get-Date).AddSeconds($Seconds)
  do {
    try {
      $response = Invoke-WebRequest -Method GET -Uri $url -UseBasicParsing -TimeoutSec 10 -SkipHttpErrorCheck
      if ([int]$response.StatusCode -eq 200) {
        Write-Host "  OK    200 $url"
        return
      }
    }
    catch {}
    Start-Sleep -Milliseconds 800
  } while ((Get-Date) -lt $deadline)

  throw "Health endpoint did not become ready in ${Seconds}s: $url"
}

function Cleanup-OldImages {
  param(
    [Parameter(Mandatory = $true)][string]$RegistryId,
    [Parameter(Mandatory = $true)][string]$RepoName,
    [int]$Keep = 5
  )

  Write-Host "==> Cleanup images (keep $Keep latest)"
  $repositoryName = "$RegistryId/$RepoName"
  try {
    $raw = yc container image list --repository-name $repositoryName --format json
    $images = @($raw | ConvertFrom-Json)
    if ($images.Count -le $Keep) {
      Write-Host "  Nothing to delete (<= $Keep images in $repositoryName)."
      return
    }

    $sorted = $images | Sort-Object { [datetime]$_.created_at } -Descending
    $toDelete = $sorted | Select-Object -Skip $Keep

    foreach ($image in $toDelete) {
      Write-Host ("  delete {0} ({1})" -f $image.id, $image.created_at)
      yc container image delete --id $image.id | Out-Null
    }
  }
  catch {
    Write-Warning "Cleanup skipped: $($_.Exception.Message)"
  }
}

function Mask-Value {
  param([string]$Value)
  if ([string]::IsNullOrWhiteSpace($Value)) { return '' }
  return '***'
}

# --------------------------- Pre-flight -------------------------------------
Write-Host '=== OPEN Project Risk :: Deploy Serverless Container ==='

Validate-Tool -Name 'yc'
Validate-Tool -Name 'docker'

$REGISTRY_ID = Get-EnvOrValue -Name 'REGISTRY_ID' -Value $REGISTRY_ID
$REPO_NAME = Get-EnvOrValue -Name 'REPO_NAME' -Value $REPO_NAME
$CONTAINER_NAME = Get-EnvOrValue -Name 'CONTAINER_NAME' -Value $CONTAINER_NAME
$CONTAINER_ID = Get-EnvOrValue -Name 'CONTAINER_ID' -Value $CONTAINER_ID
$SERVICE_ACCOUNT_ID = Get-EnvOrValue -Name 'SERVICE_ACCOUNT_ID' -Value $SERVICE_ACCOUNT_ID
$YC_FOLDER_ID = Get-YcFolderId -ConfiguredFolderId (Get-EnvOrValue -Name 'YC_FOLDER_ID' -Value $YC_FOLDER_ID)

$APP_NAME = Get-EnvOrValue -Name 'APP_NAME' -Value $APP_NAME
$API_V1_PREFIX = Get-EnvOrValue -Name 'API_V1_PREFIX' -Value $API_V1_PREFIX
$ENV = Get-EnvOrValue -Name 'ENV' -Value $ENV
$DEBUG = Get-EnvOrValue -Name 'DEBUG' -Value $DEBUG
$DATABASE_URL = Get-EnvOrValue -Name 'DATABASE_URL' -Value $DATABASE_URL
$DEMO_AUTH_ENABLED = Get-EnvOrValue -Name 'DEMO_AUTH_ENABLED' -Value $DEMO_AUTH_ENABLED
$DEMO_AUTH_USERNAME = Get-EnvOrValue -Name 'DEMO_AUTH_USERNAME' -Value $DEMO_AUTH_USERNAME
$DEMO_AUTH_PASSWORD = Get-EnvOrValue -Name 'DEMO_AUTH_PASSWORD' -Value $DEMO_AUTH_PASSWORD
$SECRET_KEY = Get-EnvOrValue -Name 'SECRET_KEY' -Value $SECRET_KEY
$SESSION_COOKIE_NAME = Get-EnvOrValue -Name 'SESSION_COOKIE_NAME' -Value $SESSION_COOKIE_NAME
$SESSION_TTL_SECONDS = Get-EnvOrValue -Name 'SESSION_TTL_SECONDS' -Value $SESSION_TTL_SECONDS

$MEMORY = Get-EnvOrValue -Name 'MEMORY' -Value $MEMORY
$CORES = [int](Get-EnvOrValue -Name 'CORES' -Value "$CORES")
$CONCURRENCY = [int](Get-EnvOrValue -Name 'CONCURRENCY' -Value "$CONCURRENCY")
$MIN_INSTANCES = [int](Get-EnvOrValue -Name 'MIN_INSTANCES' -Value "$MIN_INSTANCES")
$EXECUTION_TIMEOUT = Get-EnvOrValue -Name 'EXECUTION_TIMEOUT' -Value $EXECUTION_TIMEOUT
$HEALTH_WAIT_SECONDS = [int](Get-EnvOrValue -Name 'HEALTH_WAIT_SECONDS' -Value "$HEALTH_WAIT_SECONDS")

$requiredValues = @{
  REGISTRY_ID = $REGISTRY_ID
  REPO_NAME = $REPO_NAME
  CONTAINER_NAME = $CONTAINER_NAME
  SERVICE_ACCOUNT_ID = $SERVICE_ACCOUNT_ID
  YC_FOLDER_ID = $YC_FOLDER_ID
  APP_NAME = $APP_NAME
  API_V1_PREFIX = $API_V1_PREFIX
  ENV = $ENV
  DEBUG = $DEBUG
  DATABASE_URL = $DATABASE_URL
  DEMO_AUTH_ENABLED = $DEMO_AUTH_ENABLED
  DEMO_AUTH_USERNAME = $DEMO_AUTH_USERNAME
  DEMO_AUTH_PASSWORD = $DEMO_AUTH_PASSWORD
  SECRET_KEY = $SECRET_KEY
  SESSION_COOKIE_NAME = $SESSION_COOKIE_NAME
  SESSION_TTL_SECONDS = $SESSION_TTL_SECONDS
  MEMORY = $MEMORY
  EXECUTION_TIMEOUT = $EXECUTION_TIMEOUT
}
foreach ($item in $requiredValues.GetEnumerator()) {
  Validate-RequiredValue -Name $item.Key -Value ([string]$item.Value)
}

if ($MEMORY -notmatch '^\d+[MG]$') {
  throw "MEMORY must match '<number>M' or '<number>G'. Actual: '$MEMORY'"
}
if ($EXECUTION_TIMEOUT -notmatch '^\d+s$') {
  throw "EXECUTION_TIMEOUT must match '<seconds>s'. Actual: '$EXECUTION_TIMEOUT'"
}
if ($CORES -lt 1 -or $CONCURRENCY -lt 1 -or $MIN_INSTANCES -lt 0) {
  throw 'CORES, CONCURRENCY, and MIN_INSTANCES contain invalid values.'
}
if ($SESSION_TTL_SECONDS -notmatch '^\d+$') {
  throw "SESSION_TTL_SECONDS must be integer seconds. Actual: '$SESSION_TTL_SECONDS'"
}

$CONTAINER_ID = Resolve-ContainerId -ConfiguredContainerId $CONTAINER_ID -Name $CONTAINER_NAME -FolderId $YC_FOLDER_ID

$BUILDSTAMP = (Get-Date).ToString('yyyyMMdd-HHmmssfff')
$LOCAL_IMAGE = "${REPO_NAME}:$BUILDSTAMP"
$REMOTE_IMAGE = "cr.yandex/${REGISTRY_ID}/${REPO_NAME}:$BUILDSTAMP"
$APP_BASE = "https://$CONTAINER_ID.containers.yandexcloud.net"

Write-Host ("Folder       : {0}" -f $YC_FOLDER_ID)
Write-Host ("Container    : {0} ({1})" -f $CONTAINER_NAME, $CONTAINER_ID)
Write-Host ("Local image  : {0}" -f $LOCAL_IMAGE)
Write-Host ("Remote image : {0}" -f $REMOTE_IMAGE)
Write-Host ("DATABASE_URL : {0}" -f (Mask-Value $DATABASE_URL))
Write-Host ("Demo auth    : {0}" -f $DEMO_AUTH_ENABLED)

# --------------------------- Docker login -----------------------------------
Write-Host '==> Docker login to cr.yandex'
$token = & yc iam create-token
$token | & docker login --username iam --password-stdin cr.yandex
if ($LASTEXITCODE -ne 0) {
  throw "docker login failed with exit code $LASTEXITCODE"
}
Write-Host '  OK docker login succeeded'

# --------------------------- Build/tag/push ---------------------------------
Write-Host '==> Docker build'
& docker buildx build --load --tag $LOCAL_IMAGE .
if ($LASTEXITCODE -ne 0) {
  throw "docker buildx failed with exit code $LASTEXITCODE"
}

Write-Host '==> Docker tag'
$tagResult = Run-Proc -FilePath 'docker' -Args @('tag', $LOCAL_IMAGE, $REMOTE_IMAGE)
if ($tagResult.ExitCode -ne 0) {
  throw "docker tag failed: $($tagResult.StdErr)"
}

Write-Host '==> Docker push'
& docker push $REMOTE_IMAGE
if ($LASTEXITCODE -ne 0) {
  throw "docker push failed with exit code $LASTEXITCODE"
}

# --------------------------- Deploy revision --------------------------------
Write-Host '==> Deploy serverless container revision'
$deployArgs = @(
  'serverless', 'container', 'revision', 'deploy',
  '--container-id', $CONTAINER_ID,
  '--image', $REMOTE_IMAGE,
  '--service-account-id', $SERVICE_ACCOUNT_ID,
  '--environment', "APP_NAME=$APP_NAME",
  '--environment', "ENV=$ENV",
  '--environment', "DEBUG=$DEBUG",
  '--environment', "API_V1_PREFIX=$API_V1_PREFIX",
  '--environment', "DATABASE_URL=$DATABASE_URL",
  '--environment', "DEMO_AUTH_ENABLED=$DEMO_AUTH_ENABLED",
  '--environment', "DEMO_AUTH_USERNAME=$DEMO_AUTH_USERNAME",
  '--environment', "DEMO_AUTH_PASSWORD=$DEMO_AUTH_PASSWORD",
  '--environment', "SECRET_KEY=$SECRET_KEY",
  '--environment', "SESSION_COOKIE_NAME=$SESSION_COOKIE_NAME",
  '--environment', "SESSION_TTL_SECONDS=$SESSION_TTL_SECONDS",
  '--memory', $MEMORY,
  '--cores', "$CORES",
  '--concurrency', "$CONCURRENCY",
  '--min-instances', "$MIN_INSTANCES",
  '--execution-timeout', $EXECUTION_TIMEOUT
)
$deployResult = Run-Proc -FilePath 'yc' -Args $deployArgs -TimeoutSec 180
if ($deployResult.ExitCode -ne 0) {
  if ($deployResult.StdErr) { Write-Host $deployResult.StdErr }
  if ($deployResult.StdOut) { Write-Host $deployResult.StdOut }
  throw "yc serverless container revision deploy failed with exit code $($deployResult.ExitCode)"
}
Write-Host '  OK deploy revision completed'

Write-Host '==> Allow unauthenticated invoke'
$publicResult = Run-Proc -FilePath 'yc' -Args @(
  'serverless', 'container', 'allow-unauthenticated-invoke',
  '--id', $CONTAINER_ID
) -TimeoutSec 90
if ($publicResult.ExitCode -ne 0) {
  throw "allow-unauthenticated-invoke failed: $($publicResult.StdErr)"
}
Write-Host '  OK public invoke enabled'

# --------------------------- Smoke checks -----------------------------------
Write-Host '==> Smoke checks'
Wait-Health -BaseUrl $APP_BASE -Seconds $HEALTH_WAIT_SECONDS
Invoke-SmokeGet -Url "$APP_BASE/login" -ExpectedStatuses @(200) | Out-Null
Invoke-SmokeGet -Url "$APP_BASE$API_V1_PREFIX/projects" -ExpectedStatuses @(401) | Out-Null
$projectsResponse = Invoke-SmokeGet -Url "$APP_BASE/projects" -ExpectedStatuses @(303, 307, 308, 200) -NoRedirect
if ([int]$projectsResponse.StatusCode -in @(303, 307, 308)) {
  $location = [string]$projectsResponse.Headers.Location
  if ($location -notmatch '/login') {
    throw "Expected /projects redirect to /login, actual Location: $location"
  }
}

# --------------------------- Cleanup ----------------------------------------
Cleanup-OldImages -RegistryId $REGISTRY_ID -RepoName $REPO_NAME -Keep 5

Write-Host ''
Write-Host '=== Done ==='
Write-Host ("Image      : {0}" -f $REMOTE_IMAGE)
Write-Host ("Container  : {0}" -f $CONTAINER_ID)
Write-Host ("App        : {0}" -f $APP_BASE)
Write-Host ("Login      : {0}/login" -f $APP_BASE)
Write-Host ("Projects   : {0}/projects" -f $APP_BASE)
Write-Host ("Health     : {0}{1}/health" -f $APP_BASE, $API_V1_PREFIX)
