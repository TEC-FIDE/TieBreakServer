function CheckParameters {
    param (
        [string]$_watch
    )
    # Show help if no project name is provided
    if ($_watch -eq "-h" -or (-not $_watch -eq "" -and -not $_watch -eq "--watch" )){
        ShowHelp
        exit
    }

    # Check for required environment variables and display help if they're missing
    if (-not $env:PROJECT_NAME -or -not $env:PROJECT_DIR) {
    exit
        ShowEnvVarHelp
        exit
    }
}


function DisplayEnvironmentVariables {
    param (
        [string]$_watch
    )
    Write-Host ""
    Write-Host "Variables"  -ForegroundColor Green
    Write-Host "watch:                      $_watch"
    Write-Host ""
    Write-Host "System Environment Variables"  -ForegroundColor Green
    Write-Host "GH_REPO_ACCESS_BY_OWN_APPS: $env:GH_REPO_ACCESS_BY_OWN_APPS"
    Write-Host "MYSQL_DATABASE:             ${MYSQL_DATABASE}"
    Write-Host "MYSQL_ROOT_PASSWORD:        ${MYSQL_ROOT_PASSWORD}"
    Write-Host "PROJECT_NAME:               $env:PROJECT_NAME"
    Write-Host ""
    Write-Host "Git Information"  -ForegroundColor Green
    git branch --all
    Write-Host ""
    if ( -not $_watch -eq "--watch" ){
        Write-Host "*** Running in detached state ***"  -ForegroundColor Red
    }
}

function RebuidDocker {
    param (
        [string]$_watch
    )
    docker compose down
    docker volume prune -f
    if ($_watch -eq "--watch" ){
        Write-Host "Hello"
	    & docker compose up --build --force-recreate --watch
	} else {
        Write-Host "Hello Again"
        docker compose up -d --build --force-recreate
    # docker compose start
    }
}

function ShowEnvVarHelp {
    Write-Host "Make sure the following system environment variables are set. See the help for more detail." -ForegroundColor Cyan

    $_env_vars = @(
        @("GH_REPO_ACCESS_BY_OWN_APPS", $env:GH_REPO_ACCESS_BY_OWN_APPS),
        @("MYSQL_DATABASE", "$env:MYSQL_DATABASE"),
        @("MYSQL_ROOT_PASSWORD", "$env:MYSQL_ROOT_PASSWORD"),
        @("PROJECT_DIR", "$env:PROJECT_DIR"),
        @("PROJECT_NAME", "$env:PROJECT_NAME")
    )

    foreach ($var in $_env_vars) {
        if ([string]::IsNullOrEmpty($var[1])) {
            Write-Host $var[0] -ForegroundColor Red -NoNewline
            Write-Host " - Not Set"
        } else {
            Write-Host $var[0] -ForegroundColor Green -NoNewline
            $s = " - Set to: " + $var[1]
            Write-Host $s
        }
    }
}

function ShowHelp {
    $separator = "-" * 80
    Write-Host $separator -ForegroundColor Cyan

    # Introduction
@"
This script stops the contaonders and tell Docker Compose to build images before
starting the containers. It's useful when you've made changes to the Dockerfile
or need to ensure that the latest version of the image is used.
It also forces Docker Compose to recreate the containers even if their
configuration and image haven't changed. It's useful for ensuring a clean state
if your application's environment needs to be reset.
Docker is started in the detached state, unless the --watch option is used.

"@ | Write-Host

    Write-Host $separator -ForegroundColor Cyan

    # Environment Variables
@"
    Environment Variables:
    ----------------------
    Prior to starting the PowerShell script, ensure these environment variables are set.

    1. GH_REPO_ACCESS_BY_OWN_APPS: Your GitHub token.
    2. PROJECT_NAME:               Repository Name of the project.
"@ | Write-Host

    Write-Host $separator -ForegroundColor Cyan

    # Usage
@"
    Usage:
    ------
    vn.ps1 [--watch]
    vr.ps1 -h

    Parameters:
    1. watch: Enable the watch feature.
              Note: Docker cannot be started in the detached state.
"@ | Write-Host

    Write-Host $separator -ForegroundColor Cyan
}

# Script execution starts here
Write-Host ''
Write-Host ''
$dateTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "=[ START $dateTime ]=========================[ docker-rebuild.ps1 ]===" -ForegroundColor Blue
CheckParameters -_watch $args[0]
RebuidDocker -_watch $args[0]
DisplayEnvironmentVariables -_watch $args[0]
Write-Host '-[ END ]------------------------------------------------------------------------' -ForegroundColor Cyan
