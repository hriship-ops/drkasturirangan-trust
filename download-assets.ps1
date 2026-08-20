$assets = @{
  "logo-text.png"               = "https://www.figma.com/api/mcp/asset/9cb4f679-4561-4fc8-8686-a1314e87571e.png"
  "logo-icon.png"               = "https://www.figma.com/api/mcp/asset/45311832-5252-4024-b03b-ea4dd4acfc97.png"
  "hero-portrait.png"           = "https://www.figma.com/api/mcp/asset/a0170ba0-7b72-42dd-aba1-5b4c3962ea34.png"
  "area-space.png"              = "https://www.figma.com/api/mcp/asset/c4366840-010f-4400-9f4b-e8042a624873.png"
  "area-environment.png"        = "https://www.figma.com/api/mcp/asset/441688fd-d13f-458d-90a8-1ad7275f5dd3.png"
  "area-education.png"          = "https://www.figma.com/api/mcp/asset/d88fc3cd-6152-4246-85d6-f1f8461dcaa1.png"
  "area-publiclife.png"         = "https://www.figma.com/api/mcp/asset/ddcf030c-2494-4a09-b953-59b2f4625522.png"
  "story-card1.png"             = "https://www.figma.com/api/mcp/asset/1f921726-bf8d-4a53-967d-451f54a88b87.png"
  "story-card2.png"             = "https://www.figma.com/api/mcp/asset/934ee32c-53c2-4018-be8a-252ea45f2ded.png"
  "story-card3.png"             = "https://www.figma.com/api/mcp/asset/0c7e5dca-9a81-45f2-98f3-7b46802713b7.png"
  "rocket.png"                  = "https://www.figma.com/api/mcp/asset/2cd893b2-b709-4471-a224-9c4262ac074d.png"
  "fellowship-illustration.png" = "https://www.figma.com/api/mcp/asset/f74c40d8-f916-4dbc-a7fc-15f17d5a65f8.png"
  "fellowship-header.png"       = "https://www.figma.com/api/mcp/asset/e21811cc-12d3-433f-9fa8-035242b04756.png"
  "sir-portrait.png"            = "https://www.figma.com/api/mcp/asset/3e032791-7fa9-41d9-b638-34d348f43c99.png"
  "icon-meeting.png"            = "https://www.figma.com/api/mcp/asset/b66e4f25-a469-4b7e-8829-eb80b662a717.png"
  "icon-training.png"           = "https://www.figma.com/api/mcp/asset/109a0269-f865-4d43-8acb-a5c28b15c63d.png"
  "icon-gift.png"               = "https://www.figma.com/api/mcp/asset/7f3b3bc9-df8e-4eba-afe2-2991ec234c4e.png"
  "icon-goal.png"               = "https://www.figma.com/api/mcp/asset/ea83aa08-eb94-4e83-abe6-ff1e9f582dba.png"
  "icon-gforms.png"             = "https://www.figma.com/api/mcp/asset/c50e4a0c-3ac6-473a-8f6b-718aaf75398c.png"
  "icon-resume.png"             = "https://www.figma.com/api/mcp/asset/b22cb1fc-38c1-4781-ab49-2cbf47a87034.png"
  "icon-analyze.png"            = "https://www.figma.com/api/mcp/asset/48b9128d-bf5c-440d-ae9a-ac9bfe7612fe.png"
  "icon-person.png"             = "https://www.figma.com/api/mcp/asset/22d446fb-b67a-4e54-a926-1c9d61bd830c.png"
  "icon-schedule.png"           = "https://www.figma.com/api/mcp/asset/23d2ecf2-05d2-4cc8-bfbe-8ef85d9952a2.png"
  "doc-icon.png"                = "https://www.figma.com/api/mcp/asset/29b13961-981b-4528-b1ba-5d5e9a3496a4.png"
  # Vision & Mission page (node 682:31)
  "vision-portrait.png"         = "https://www.figma.com/api/mcp/asset/6bd3bfba-8283-4c2c-a2f7-b8681890ac8e.png"
  "vm-focus-1.png"              = "https://www.figma.com/api/mcp/asset/e84fad2b-d252-4402-bb95-993973e9e95a.png"
  "vm-focus-2.png"              = "https://www.figma.com/api/mcp/asset/9c2ab992-8ea6-4042-b664-11ff83bd6d9f.png"
  "vm-focus-3.png"              = "https://www.figma.com/api/mcp/asset/25ec6826-40ac-48dd-9d05-8e2dcb52ba3b.png"
  "vm-focus-4.png"              = "https://www.figma.com/api/mcp/asset/4583965c-1363-4522-9dfc-d6f36c8abe1e.png"
  # Dr Kasturirangan's Life page (node 650:56) — URLs refreshed 2026-08-20
  "kk-illustration.svg"         = "https://www.figma.com/api/mcp/asset/d25b6164-4e83-419e-b435-db9e787cae85.svg"
  "kk-photo-school.png"         = "https://www.figma.com/api/mcp/asset/ff6f3600-6ade-4ebe-b960-cb0c8450e5bf.png"
  "kk-photo-1961.png"           = "https://www.figma.com/api/mcp/asset/4c67d171-02fa-4cec-8b67-785f2f8d20a4.png"
  "kk-photo-1963.png"           = "https://www.figma.com/api/mcp/asset/d0c4db01-c289-462b-9ef6-6481c80ad385.png"
  "kk-photo-1969.png"           = "https://www.figma.com/api/mcp/asset/006e253b-ab6a-4819-8c91-3ac5be9a2415.png"
  "kk-photo-isro.png"           = "https://www.figma.com/api/mcp/asset/d837ba04-6915-4d3b-96bd-743942d31314.png"
}

$dir = "C:\appdev\drk\assets\images"
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }

foreach ($name in $assets.Keys) {
  $out = Join-Path $dir $name
  try {
    Invoke-WebRequest -Uri $assets[$name] -OutFile $out -UseBasicParsing -TimeoutSec 30
    Write-Output "OK   $name"
  } catch {
    $errMsg = $_.Exception.Message
    Write-Output "FAIL $name - $errMsg"
  }
}
Write-Output "Done."
