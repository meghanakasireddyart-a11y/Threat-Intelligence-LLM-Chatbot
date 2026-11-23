"""Threat Intelligence Knowledge Base and Seed Data

Curated threat data across platforms (Linux, Windows, MacOS, Android, iOS)
categorized by threat lifecycle status:
  - Anticipated: Early warning, emerging zero-days, predictive attack surfaces
  - Active: Currently exploited in the wild, active campaigns, botnets
  - Evolving: Polymorphic malware, adapting APTs, mutating evasion techniques
  - Resolved: Patched CVEs, neutralized exploits, published workarounds
"""

THREAT_RECORDS = [
    # --- LINUX THREATS ---
    {
        "threat_id": "THREAT-LNX-001",
        "name": "xz-utils Supply Chain Backdoor (CVE-2024-3094)",
        "platform": "Linux",
        "status": "Resolved",
        "severity": "Critical",
        "cve_id": "CVE-2024-3094",
        "cvss_score": 10.0,
        "description": "Malicious code injected into upstream tarballs of xz-utils liblzma modifying sshd authentication routines to enable remote code execution via unauthorized public keys.",
        "attack_vector": "Supply Chain Compromise",
        "indicators_of_compromise": [
            "liblzma.so.5.6.0",
            "liblzma.so.5.6.1",
            "SIGBUS in OpenSSH daemon during authentication",
            "Hash SHA256: 3192498466d821fb07219c211f69e383ec104e7d06431e16ec4d4238c668a30a"
        ],
        "mitigation_steps": (
            "1. Check installed xz version: xz --version\n"
            "2. Downgrade xz-utils to 5.4.x or upgrade to fixed 5.6.1-patch:\n"
            "   sudo apt-get update && sudo apt-get install --only-upgrade xz-utils liblzma5\n"
            "3. Restart OpenSSH service: sudo systemctl restart ssh\n"
            "4. Verify sshd linking: ldd $(which sshd) | grep lzma"
        ),
        "mitigation_script": "apt-get update && apt-get --only-upgrade install -y xz-utils liblzma5 && systemctl restart ssh",
        "first_detected": "2024-03-29T10:00:00Z",
        "last_updated": "2024-04-15T18:30:00Z"
    },
    {
        "threat_id": "THREAT-LNX-002",
        "name": "SSH Snake Self-Modifying Worm",
        "platform": "Linux",
        "status": "Active",
        "severity": "High",
        "cve_id": "CVE-2023-48795",
        "cvss_score": 7.5,
        "description": "Self-replicating worm that crawls Linux systems looking for private SSH keys in shell histories, bashrc, and .ssh directories, dynamically generating traversal paths across secondary subnets.",
        "attack_vector": "Credential Harvesting & Lateral Movement",
        "indicators_of_compromise": [
            "Outbound SSH connections from non-standard system processes",
            "File modifications to ~/.ssh/known_hosts and /etc/hosts",
            "Process signature executing base64-decoded bash scripts in /dev/shm"
        ],
        "mitigation_steps": (
            "1. Terminate suspicious bash processes running from /dev/shm or /tmp:\n"
            "   pkill -f '/dev/shm/.*ssh'\n"
            "2. Revoke and rotate all SSH keys across all reachable hosts\n"
            "3. Restrict file permissions on ~/.ssh: chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_*\n"
            "4. Enforce strict passphrase protection and hardware tokens (FIDO2) for SSH"
        ),
        "mitigation_script": "chmod 700 ~/.ssh && chmod 600 ~/.ssh/* && pkill -9 -f '/dev/shm'",
        "first_detected": "2024-01-12T08:00:00Z",
        "last_updated": "2024-06-10T14:20:00Z"
    },
    {
        "threat_id": "THREAT-LNX-003",
        "name": "eBPF Rootkit Stealth Kernel Hooks",
        "platform": "Linux",
        "status": "Evolving",
        "severity": "Critical",
        "cve_id": "CVE-2024-21626",
        "cvss_score": 8.6,
        "description": "Adversaries leveraging extended Berkeley Packet Filter (eBPF) tracepoints and kprobes to manipulate syscall returns, stealthily hiding processes, network sockets, and file activity from standard diagnostic tools (ps, netstat, lsof).",
        "attack_vector": "Kernel-level Privilege Persistence",
        "indicators_of_compromise": [
            "Unexpected eBPF program IDs loaded into kernel without systemd-bpf or monitoring agent tag",
            "Discrepancy between raw disk read and /proc filesystem listings",
            "BPF map size growth in unprivileged namespaces"
        ],
        "mitigation_steps": (
            "1. Inspect active BPF programs: sudo bpftool prog list\n"
            "2. Restrict unprivileged eBPF access:\n"
            "   sysctl -w kernel.unprivileged_bpf_disabled=1\n"
            "   echo 'kernel.unprivileged_bpf_disabled=1' >> /etc/sysctl.d/99-bpf-hardening.conf\n"
            "3. Enforce kernel module signature verification: sysctl -w kernel.modules_disabled=1"
        ),
        "mitigation_script": "sysctl -w kernel.unprivileged_bpf_disabled=1 && sysctl -p",
        "first_detected": "2024-05-18T12:00:00Z",
        "last_updated": "2024-07-02T16:45:00Z"
    },
    {
        "threat_id": "THREAT-LNX-004",
        "name": "Predictive Post-Quantum Cryptanalysis of TLS Sessions",
        "platform": "Linux",
        "status": "Anticipated",
        "severity": "Medium",
        "cve_id": "CVE-PREDICT-2026-01",
        "cvss_score": 6.0,
        "description": "Anticipated 'Harvest Now, Decrypt Later' threat targeting Linux server TLS infrastructure. Adversaries record encrypted enterprise traffic awaiting scalable Shor algorithm implementations.",
        "attack_vector": "Cryptographic Degradation",
        "indicators_of_compromise": [
            "High-volume anomalous egress packet mirroring to unmapped cloud storage",
            "Legacy RSA-2048 key exchanges in public service endpoints"
        ],
        "mitigation_steps": (
            "1. Update OpenSSL to 3.2+ supporting hybrid post-quantum key exchange (Kyber/ML-KEM)\n"
            "2. Configure nginx / Apache to prefer X25519Kyber768Draft00 algorithms\n"
            "3. Enforce forward secrecy with ephemeral diffie-hellman suites"
        ),
        "mitigation_script": "openssl version && update-crypto-policies --set FUTURE",
        "first_detected": "2024-06-01T00:00:00Z",
        "last_updated": "2024-07-15T09:10:00Z"
    },

    # --- WINDOWS THREATS ---
    {
        "threat_id": "THREAT-WIN-001",
        "name": "Windows Wi-Fi Driver Remote Code Execution (CVE-2024-30078)",
        "platform": "Windows",
        "status": "Resolved",
        "severity": "High",
        "cve_id": "CVE-2024-30078",
        "cvss_score": 8.8,
        "description": "Unauthenticated remote code execution flaw in the Windows Wi-Fi network driver. An attacker within radio proximity can send malicious beacons to execute arbitrary commands without user interaction.",
        "attack_vector": "Wireless Adjacent Network Vector",
        "indicators_of_compromise": [
            "Kernel panic (BSOD) in nwifi.sys",
            "Abnormal 802.11 management frames recorded by wireless monitoring",
            "Crash dump referencing WLAN_EXT_REASON_CODE"
        ],
        "mitigation_steps": (
            "1. Deploy Microsoft Security Update KB5039211 (June 2024 Patch Tuesday)\n"
            "2. Alternatively, disable Wi-Fi adapters when connected via ethernet:\n"
            "   Disable-NetAdapter -Name 'Wi-Fi' -Confirm:$false\n"
            "3. Enforce 802.1X enterprise network authentication policies"
        ),
        "mitigation_script": "Install-WindowsUpdate -KBArticleID KB5039211 -AcceptAll -AutoReboot",
        "first_detected": "2024-06-11T17:00:00Z",
        "last_updated": "2024-06-25T11:00:00Z"
    },
    {
        "threat_id": "THREAT-WIN-002",
        "name": "Qakbot / BlackBasta Living-off-the-Land Injections",
        "platform": "Windows",
        "status": "Active",
        "severity": "Critical",
        "cve_id": "CVE-2024-21412",
        "cvss_score": 8.1,
        "description": "Active ransomware delivery chain exploiting Internet Shortcut (.URL) file flaws to bypass SmartScreen, executing encoded PowerShell scripts that inject payloads into explorer.exe and svchost.exe.",
        "attack_vector": "Social Engineering & LOLBins",
        "indicators_of_compromise": [
            "Process explorer.exe spawning powershell.exe with -encodedCommand",
            "Registry Run key addition under HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "Network traffic to known bulletproof hoster IPs on TCP port 443"
        ],
        "mitigation_steps": (
            "1. Block outbound SMB and RPC egress at firewall (TCP 135, 139, 445)\n"
            "2. Enable Attack Surface Reduction (ASR) rules:\n"
            "   Set-MpPreference -AttackSurfaceReductionRules_Ids D4F940AB-401B-4EFC-AADC-AD5F3C50688A -AttackSurfaceReductionRules_Actions Enabled\n"
            "3. Enforce PowerShell Constrained Language Mode via AppLocker or WDAC"
        ),
        "mitigation_script": "Set-MpPreference -AttackSurfaceReductionRules_Ids D4F940AB-401B-4EFC-AADC-AD5F3C50688A -AttackSurfaceReductionRules_Actions Enabled",
        "first_detected": "2024-02-13T09:00:00Z",
        "last_updated": "2024-07-10T15:30:00Z"
    },
    {
        "threat_id": "THREAT-WIN-003",
        "name": "Polymorphic UEFI Bootkit Persistence (BlackLotus Variant)",
        "platform": "Windows",
        "status": "Evolving",
        "severity": "Critical",
        "cve_id": "CVE-2023-24932",
        "cvss_score": 7.8,
        "description": "Evolving UEFI bootkit that bypasses Secure Boot by exploiting revoked boot managers. It disables Hypervisor-Protected Code Integrity (HVCI) and BitLocker before kernel initialization.",
        "attack_vector": "Pre-Boot Firmware Compromise",
        "indicators_of_compromise": [
            "Unauthorized ESP EFI bootloader file: \\EFI\\Microsoft\\Boot\\bootmgfw.efi modified",
            "Disabled Defender Credential Guard via registry registry modification",
            "Absence of measured boot log records in PCR[7]"
        ],
        "mitigation_steps": (
            "1. Apply Windows Security Update for CVE-2023-24932\n"
            "2. Update Secure Boot DBX revocation list:\n"
            "   Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Secureboot' -Name 'AvailableUpdates' -Value 0x40\n"
            "3. Verify firmware TPM 2.0 PCR measurements"
        ),
        "mitigation_script": "reg add HKLM\\SYSTEM\\CurrentControlSet\\Control\\Secureboot /v AvailableUpdates /t REG_DWORD /d 64 /f",
        "first_detected": "2023-05-09T14:00:00Z",
        "last_updated": "2024-06-20T17:15:00Z"
    },
    {
        "threat_id": "THREAT-WIN-004",
        "name": "CoPilot / Recall Local Data Scraping Exposure",
        "platform": "Windows",
        "status": "Anticipated",
        "severity": "High",
        "cve_id": "CVE-ANTICIPATED-2026-WIN",
        "cvss_score": 7.2,
        "description": "Anticipated exploitation vector where unprivileged local malware extracts optical character recognition (OCR) and snapshot SQLite databases generated by local AI desktop surveillance features.",
        "attack_vector": "Local Data Infiltration",
        "indicators_of_compromise": [
            "Access to %LOCALAPPDATA%\\CoreAIPlatform.00\\UKP\\{GUID}\\snapshot.db by non-system apps",
            "Exfiltration of high-entropy compressed SQLite artifacts"
        ],
        "mitigation_steps": (
            "1. Disable Windows Recall feature via Group Policy:\n"
            "   Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsAI' -Name 'DisableAIDataAnalysis' -Value 1\n"
            "2. Restrict Read ACLs on user profile CoreAIPlatform folders\n"
            "3. Enforce BitLocker full volume encryption"
        ),
        "mitigation_script": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsAI /v DisableAIDataAnalysis /t REG_DWORD /d 1 /f",
        "first_detected": "2024-06-05T11:00:00Z",
        "last_updated": "2024-07-01T12:00:00Z"
    },

    # --- MACOS THREATS ---
    {
        "threat_id": "THREAT-MAC-001",
        "name": "RustBucket Apple Silicon Native Infostealer",
        "platform": "MacOS",
        "status": "Active",
        "severity": "High",
        "cve_id": "CVE-2024-27842",
        "cvss_score": 7.8,
        "description": "Mach-O compiled multistage malware compiled natively for ARM64 (Apple Silicon). Masquerades as legitimate PDF viewers or Webex updates, harvesting Keychain entries and browser cookies.",
        "attack_vector": "Trojanized Application Delivery",
        "indicators_of_compromise": [
            "Unsigned dylib loaded into /Library/LaunchAgents/com.apple.updater.plist",
            "Outbound beaconing to dynamic DNS domains over HTTPS port 8443",
            "Mach-O binary with ad-hoc code signature not notarized by Apple"
        ],
        "mitigation_steps": (
            "1. Unload and delete malicious LaunchAgent:\n"
            "   launchctl bootout gui/$(id -u)/com.apple.updater\n"
            "   rm -f ~/Library/LaunchAgents/com.apple.updater.plist\n"
            "2. Enforce Gatekeeper strict enforcement: spctl --master-enable\n"
            "3. Audit Keychain access logs via Console.app"
        ),
        "mitigation_script": "spctl --master-enable && rm -f ~/Library/LaunchAgents/com.apple.updater.plist",
        "first_detected": "2024-02-18T10:00:00Z",
        "last_updated": "2024-06-18T16:00:00Z"
    },
    {
        "threat_id": "THREAT-MAC-002",
        "name": "XNU Kernel Double-Free Privilege Escalation",
        "platform": "MacOS",
        "status": "Resolved",
        "severity": "Critical",
        "cve_id": "CVE-2024-27878",
        "cvss_score": 9.1,
        "description": "Kernel memory corruption vulnerability in XNU packet filter handling allowing an attacker with local execution to break macOS sandbox isolation and obtain root privileges.",
        "attack_vector": "Local Privilege Escalation",
        "indicators_of_compromise": [
            "Kernel panic log with backtrace in pf_test() or pf_match_rule()",
            "Unexpected root shell spawned with PPID of standard desktop app"
        ],
        "mitigation_steps": (
            "1. Upgrade macOS to version 14.5 (Sonoma) or 13.6.7 (Ventura):\n"
            "   softwareupdate --install --all --restart\n"
            "2. Verify System Integrity Protection (SIP) is active: csrutil status"
        ),
        "mitigation_script": "softwareupdate -ia --verbose",
        "first_detected": "2024-04-02T13:00:00Z",
        "last_updated": "2024-05-20T10:00:00Z"
    },
    {
        "threat_id": "THREAT-MAC-003",
        "name": "Synthetic Click Injection via Accessibility API",
        "platform": "MacOS",
        "status": "Evolving",
        "severity": "High",
        "cve_id": "CVE-2024-44123",
        "cvss_score": 7.4,
        "description": "Evolving technique where malicious background utilities exploit Accessibility and Screen Recording permissions to simulate programmatic clicks on TCC (Transparency, Consent, and Control) dialogs.",
        "attack_vector": "TCC Permission Hijacking",
        "indicators_of_compromise": [
            "Rapid synthetic mouse events without human input hardware interrupt",
            "Modifications to TCC.db in /Library/Application Support/com.apple.TCC/"
        ],
        "mitigation_steps": (
            "1. Audit granted Accessibility apps in System Settings > Privacy & Security > Accessibility\n"
            "2. Reset TCC database for accessibility: tccutil reset Accessibility\n"
            "3. Enforce Managed Device Profiles forbidding automatic TCC grants"
        ),
        "mitigation_script": "tccutil reset Accessibility && tccutil reset ScreenCapture",
        "first_detected": "2024-05-11T15:00:00Z",
        "last_updated": "2024-07-08T18:10:00Z"
    },

    # --- ANDROID THREATS ---
    {
        "threat_id": "THREAT-AND-001",
        "name": "GoldPickaxe Facial Biometric Harvesting Trojan",
        "platform": "Android",
        "status": "Active",
        "severity": "Critical",
        "cve_id": "CVE-2024-32896",
        "cvss_score": 8.9,
        "description": "Android banking trojan that abuses Accessibility Services to record user face scans, intercept SMS OTPs, and forge identity verification on mobile banking platforms.",
        "attack_vector": "Accessibility Service Abuse & Sideloading",
        "indicators_of_compromise": [
            "App requesting BIND_ACCESSIBILITY_SERVICE under fake 'System Utility' name",
            "Hidden camera service foreground notification suppression",
            "C2 traffic to WebSocket endpoints transmitting base64 biometric payloads"
        ],
        "mitigation_steps": (
            "1. Revoke Accessibility permissions for untrusted apps in Settings > Accessibility\n"
            "2. Uninstall malicious APK via ADB or Safe Mode:\n"
            "   adb uninstall com.mobile.system.utility\n"
            "3. Enable Google Play Protect and enforce 'Verify Apps over USB'\n"
            "4. Contact financial institutions to reset biometric credentials"
        ),
        "mitigation_script": "adb shell pm disable-user --user 0 com.mobile.system.utility && adb uninstall com.mobile.system.utility",
        "first_detected": "2024-02-01T12:00:00Z",
        "last_updated": "2024-06-28T09:40:00Z"
    },
    {
        "threat_id": "THREAT-AND-002",
        "name": "Android Qualcomm Adreno GPU Kernel Memory Corruption",
        "platform": "Android",
        "status": "Resolved",
        "severity": "High",
        "cve_id": "CVE-2024-4971",
        "cvss_score": 8.4,
        "description": "Memory corruption flaw in Qualcomm Adreno GPU driver allowing untrusted Chrome renderers or sandboxed apps to achieve physical memory read/write access.",
        "attack_vector": "Sandbox Escape via Hardware Driver",
        "indicators_of_compromise": [
            "Unexpected kernel crash log pointing to kgsl_sharedmem_page_alloc()",
            "Anomalous OpenGL ES texture allocation sizes in system logcat"
        ],
        "mitigation_steps": (
            "1. Apply Android Security Patch Level 2024-06-01 or later\n"
            "2. Update Google Play System components via Settings > Security & Privacy\n"
            "3. Enable strict isolatedProcess flags in browser apps"
        ),
        "mitigation_script": "adb shell am start -a android.settings.SYSTEM_UPDATE_SETTINGS",
        "first_detected": "2024-03-15T08:00:00Z",
        "last_updated": "2024-06-15T11:00:00Z"
    },
    {
        "threat_id": "THREAT-AND-003",
        "name": "RCS Automated Message Spreading Botnet",
        "platform": "Android",
        "status": "Evolving",
        "severity": "Medium",
        "cve_id": "CVE-EVOLVE-AND-RCS",
        "cvss_score": 6.8,
        "description": "Evolving campaign using Rich Communication Services (RCS) protocols to automatically deliver polymorphic phishing URLs with end-to-end encryption bypassing carrier-side SMS spam filters.",
        "attack_vector": "Encrypted P2P Mobile Phishing",
        "indicators_of_compromise": [
            "High rate of outbound RCS packets generated during standby",
            "Unrecognized active sessions in Google Messages Web pairing"
        ],
        "mitigation_steps": (
            "1. Temporarily disable RCS Chats in Google Messages Settings > RCS chats\n"
            "2. Terminate all unpaired Web sessions in Messages for Web\n"
            "3. Enforce carrier spam protection filter settings"
        ),
        "mitigation_script": "adb shell am force-stop com.google.android.apps.messaging",
        "first_detected": "2024-05-22T14:30:00Z",
        "last_updated": "2024-07-12T13:20:00Z"
    },

    # --- IOS THREATS ---
    {
        "threat_id": "THREAT-IOS-001",
        "name": "Operation Triangulation Zero-Click iMessage Exploit",
        "platform": "iOS",
        "status": "Resolved",
        "severity": "Critical",
        "cve_id": "CVE-2023-41990",
        "cvss_score": 9.8,
        "description": "Zero-click iMessage attachment exploit chaining font parsing vulnerabilities with undocumented Apple A-series SoC hardware MMIO registers to execute kernel payloads and install Pegasus-style spyware.",
        "attack_vector": "Zero-Click iMessage Attachment",
        "indicators_of_compromise": [
            "Hidden attachment file named attachment.png with malformed TrueType font table",
            "Unexpected crash logs of MobileSMS daemon",
            "Anomalous background network connections to cloud hosting nodes over TLS"
        ],
        "mitigation_steps": (
            "1. Update iOS to version 17.0.1 or later immediately\n"
            "2. Turn on Lockdown Mode in Settings > Privacy & Security > Lockdown Mode:\n"
            "   Blocks message attachments, complex web technologies, and incoming FaceTime requests\n"
            "3. Reboot device daily to clear volatile memory implants"
        ),
        "mitigation_script": "echo 'Enable Lockdown Mode via iOS Settings > Privacy & Security > Lockdown Mode'",
        "first_detected": "2023-09-15T18:00:00Z",
        "last_updated": "2024-03-10T12:00:00Z"
    },
    {
        "threat_id": "THREAT-IOS-002",
        "name": "WebKit Type Confusion Remote Code Execution",
        "platform": "iOS",
        "status": "Active",
        "severity": "High",
        "cve_id": "CVE-2024-27834",
        "cvss_score": 8.8,
        "description": "Actively exploited type confusion vulnerability in WebKit JIT compiler. Processing maliciously crafted web content leads to arbitrary code execution within the Safari content process sandbox.",
        "attack_vector": "Web Browser Drive-by Download",
        "indicators_of_compromise": [
            "Safari crash logs showing SIGSEGV in JSC::JITCompiler::compile()",
            "Redirection to domain names registered on newly minted TLDs (.top, .xyz)"
        ],
        "mitigation_steps": (
            "1. Update device to iOS 17.5.1 / iPadOS 17.5.1\n"
            "2. Enable Safari Advanced Tracking and Fingerprinting Protection\n"
            "3. Disable JavaScript for untrusted networks in Settings > Safari > Advanced"
        ),
        "mitigation_script": "echo 'Install iOS 17.5.1 via Settings > General > Software Update'",
        "first_detected": "2024-04-18T10:00:00Z",
        "last_updated": "2024-06-22T17:00:00Z"
    },
    {
        "threat_id": "THREAT-IOS-003",
        "name": "Side-Channel Key Extraction via Neural Engine",
        "platform": "iOS",
        "status": "Anticipated",
        "severity": "Medium",
        "cve_id": "CVE-ANTICIPATED-2026-ANE",
        "cvss_score": 6.5,
        "description": "Anticipated side-channel vulnerability where unprivileged apps measure microarchitectural timing and power variance in Apple Neural Engine (ANE) tensor computations to reconstruct cryptographic keys.",
        "attack_vector": "Microarchitectural Side-Channel",
        "indicators_of_compromise": [
            "Continuous background ANE execution cycles by foreground utility apps",
            "High-precision timer queries using mach_absolute_time() in loops"
        ],
        "mitigation_steps": (
            "1. Enforce App Store review gating on CoreML / ANE timing precision\n"
            "2. Implement constant-time blinding in high-security crypto modules\n"
            "3. Monitor background battery and neural compute drain per application"
        ),
        "mitigation_script": "echo 'Verify background app refresh is disabled for unverified apps'",
        "first_detected": "2024-06-12T09:00:00Z",
        "last_updated": "2024-07-05T14:00:00Z"
    }
]

# Knowledge base texts for RAG vector search
KNOWLEDGE_DOCUMENTS = [
    {
        "title": "Threat Intelligence Lifecycle: Anticipated, Active, Evolving, Resolved",
        "content": (
            "Threat Intelligence is systematically structured across four operational lifecycle states. "
            "Anticipated Threats represent early predictive warnings, zero-day research chatter, emerging attack vectors, "
            "and cryptographic deprecation before widespread weaponization occurs. Early mitigation focuses on policy hardening, "
            "cipher upgrade (e.g. Post-Quantum TLS), and attack surface reduction. "
            "Active Threats are actively exploited in the wild, driven by cybercrime syndicates and state-sponsored APTs. "
            "Mitigation requires immediate perimeter containment, signature blocking, process termination, and credential revocation. "
            "Evolving Threats are polymorphic, adapting malware families, living-off-the-land techniques (LOLBins), eBPF stealth rootkits, "
            "and evasion mechanisms that modify behaviors to circumvent standard endpoint detection. Mitigation requires behavioral analysis, "
            "kernel auditing, and zero-trust verification. "
            "Resolved Threats are historical or neutralized vulnerabilities with verified vendor patches, CVE remediations, and "
            "standardized security configurations. Continuous patching, regression verification, and vulnerability scanning ensure they remain closed."
        )
    },
    {
        "title": "Platform Mitigation Guide: Linux Threat Defense",
        "content": (
            "Linux security posture relies on least-privilege principles, kernel defense, and package integrity. "
            "For supply chain vulnerabilities like xz-utils (CVE-2024-3094), verify package signatures and downgrade or upgrade to "
            "untainted versions using apt-get or dnf, followed by sshd daemon restarts. "
            "Against self-propagating SSH worms, secure private keys with chmod 600, disable password authentication in /etc/ssh/sshd_config, "
            "and terminate illicit /dev/shm processes. "
            "For kernel-level eBPF threats (CVE-2024-21626), restrict unprivileged BPF via sysctl kernel.unprivileged_bpf_disabled=1 "
            "and monitor loaded programs with bpftool. "
            "For post-quantum preparedness, update OpenSSL to 3.2+ and adopt hybrid Kyber key exchange suites."
        )
    },
    {
        "title": "Platform Mitigation Guide: Windows Security Hardening",
        "content": (
            "Windows threat mitigation combines monthly cumulative updates (Patch Tuesday), Attack Surface Reduction (ASR) rules, and "
            "firmware protection. "
            "For wireless RCE vulnerabilities like CVE-2024-30078, deploy Windows Security Update KB5039211 or temporarily disable Wi-Fi adapters "
            "using Disable-NetAdapter. "
            "Against living-off-the-land malware (Qakbot, BlackBasta, CVE-2024-21412), enable Defender ASR rules, enforce PowerShell "
            "ConstrainedLanguage mode, and block outbound SMB (TCP 445). "
            "For UEFI bootkits (BlackLotus, CVE-2023-24932), update the Secure Boot DBX revocation list via registry AvailableUpdates and "
            "verify TPM 2.0 PCR[7] measurements. "
            "For Windows AI and Recall data protection, disable DisableAIDataAnalysis under HKLM Policies."
        )
    },
    {
        "title": "Platform Mitigation Guide: MacOS Endpoint Security",
        "content": (
            "macOS defense leverages System Integrity Protection (SIP), Gatekeeper, and Transparency, Consent, and Control (TCC). "
            "Against native Apple Silicon infostealers (RustBucket, CVE-2024-27842), inspect ~/Library/LaunchAgents/, unload unauthorized "
            "daemons via launchctl bootout, and enforce Gatekeeper with spctl --master-enable. "
            "For XNU kernel memory corruption (CVE-2024-27878), install macOS 14.5+ updates using softwareupdate -ia. "
            "Against Accessibility synthetic click injections (CVE-2024-44123), reset compromised permissions using tccutil reset Accessibility."
        )
    },
    {
        "title": "Platform Mitigation Guide: Mobile Defense (Android & iOS)",
        "content": (
            "Mobile threat intelligence demands strict permission controls and system updates. "
            "On Android, banking trojans like GoldPickaxe abuse Accessibility services; remediate by revoking BIND_ACCESSIBILITY_SERVICE "
            "and uninstalling unauthorized packages via adb shell pm disable-user. Apply monthly security patch levels to resolve "
            "GPU driver flaws (CVE-2024-4971). "
            "On iOS, defend against zero-click iMessage exploits (CVE-2023-41990) by updating iOS and enabling Lockdown Mode in Settings. "
            "For WebKit type confusion flaws (CVE-2024-27834), install iOS 17.5.1 and activate Advanced Tracking and Fingerprinting Protection."
        )
    },
    {
        "title": "Automated Vulnerability Scanning and Mitigation Protocol",
        "content": (
            "The background scanner service continuously inspects the local runtime and project environment. "
            "Scanning vectors include: vulnerable dependencies in requirements.txt, world-writable directories, exposed debugging ports, "
            "unquoted service paths, unpatched CVE signatures, and weak SSH or registry permissions. "
            "Upon detecting a vulnerability, the scanner generates a structured record with CVE reference, severity, and remediation script. "
            "To prevent operational disruption, mitigations require conversational user confirmation over chat before execution. "
            "Once confirmed, the bot applies the exact mitigation script, validates system state, and updates the threat status to Resolved in MongoDB."
        )
    }
]
