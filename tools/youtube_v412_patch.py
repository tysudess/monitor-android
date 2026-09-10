#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "source")

def replace(path, old, new, count=1):
    p = root / path
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"guard failed: {path}: {old[:120]!r}")
    p.write_text(text.replace(old, new, count), encoding="utf-8")

# New build number for the YouTube corrections.
replace("app/build.gradle.kts", 'versionCode = 411\n        versionName = "4.1.1"', 'versionCode = 412\n        versionName = "4.1.2"')

catalog = "app/src/main/java/br/com/monitordenoticias/android/VideoSourceCatalog.kt"
replace(
    catalog,
    'youtube("youtube-g1", "g1", "@g1", listOf("g1", "G1 Notícias", "G1 Jornalismo")),',
    'youtube("youtube-g1", "g1", "UCaGmdJSSiR7fkh2A-c6emsA", listOf("g1", "G1 Notícias", "G1 Jornalismo")),\n        youtube("youtube-domingo-espetacular", "Domingo Espetacular", "@domingoespetacular", listOf("Domingo Espetacular", "Record", "Record TV")),',
)
replace(
    catalog,
    '''    private fun youtube(id: String, label: String, handle: String, aliases: List<String>): VideoSource = VideoSource(
        id = id,
        name = "YouTube • $label",
        group = "YouTube oficial • $label",
        landingUrl = "https://www.youtube.com/$handle/videos",
        linkHints = listOf("/watch"),
        aliases = aliases,
        youtubeHandle = handle
    )''',
    '''    private fun youtube(id: String, label: String, handle: String, aliases: List<String>): VideoSource {
        val channelPath = if (handle.startsWith("UC")) "channel/$handle" else handle
        return VideoSource(
            id = id,
            name = "YouTube • $label",
            group = "YouTube oficial • $label",
            landingUrl = "https://www.youtube.com/$channelPath/videos",
            linkHints = listOf("/watch"),
            aliases = aliases,
            youtubeHandle = handle
        )
    }''',
)

repo = "app/src/main/java/br/com/monitordenoticias/android/VideoRepository.kt"
replace(
    repo,
    '''    private fun fetchYoutube(source: VideoSource, capturedAt: Long): List<VideoItem> {
        val handle = source.youtubeHandle.removePrefix("@")
        val channelPage = Jsoup.connect("https://www.youtube.com/@$handle/videos")
            .userAgent("Mozilla/5.0 (Linux; Android 14) MonitorNoticias/3.0.7")
            .timeout(14_000)
            .get()
            .html()

        val channelId = YOUTUBE_CHANNEL_ID_REGEXES.asSequence()
            .mapNotNull { regex -> regex.find(channelPage)?.groupValues?.getOrNull(1) }
            .firstOrNull { it.startsWith("UC") }
            ?: return emptyList()''',
    '''    private fun fetchYoutube(source: VideoSource, capturedAt: Long): List<VideoItem> {
        val identifier = source.youtubeHandle.trim()
        val channelId = if (identifier.startsWith("UC")) {
            identifier
        } else {
            val handle = identifier.removePrefix("@")
            val channelPage = Jsoup.connect("https://www.youtube.com/@$handle/videos")
                .userAgent("Mozilla/5.0 (Linux; Android 14) MonitorNoticias/4.1.2")
                .timeout(14_000)
                .get()
                .html()

            YOUTUBE_CHANNEL_ID_REGEXES.asSequence()
                .mapNotNull { regex -> regex.find(channelPage)?.groupValues?.getOrNull(1) }
                .firstOrNull { it.startsWith("UC") }
                ?: return emptyList()
        }''',
)

# One-shot migration so upgrades also receive the two newly verified YouTube sources.
vm = "app/src/main/java/br/com/monitordenoticias/android/VideoViewModel.kt"
replace(
    vm,
    '''        if (!prefs.getBoolean(KEY_YOUTUBE_283_MIGRATED, false)) {
            selected = selected + VideoSourceCatalog.youtubeOfficialIds
            editor.putBoolean(KEY_YOUTUBE_283_MIGRATED, true)
            changed = true
        }''',
    '''        if (!prefs.getBoolean(KEY_YOUTUBE_283_MIGRATED, false)) {
            selected = selected + VideoSourceCatalog.youtubeOfficialIds
            editor.putBoolean(KEY_YOUTUBE_283_MIGRATED, true)
            changed = true
        }
        if (!prefs.getBoolean(KEY_YOUTUBE_412_MIGRATED, false)) {
            selected = selected + setOf("youtube-g1", "youtube-domingo-espetacular")
            editor.putBoolean(KEY_YOUTUBE_412_MIGRATED, true)
            changed = true
        }''',
)
replace(
    vm,
    'const val KEY_YOUTUBE_283_MIGRATED = "video_v283_youtube_sources_added"',
    'const val KEY_YOUTUBE_283_MIGRATED = "video_v283_youtube_sources_added"\n        const val KEY_YOUTUBE_412_MIGRATED = "video_v412_youtube_sources_added"',
)
replace(
    vm,
    '.putBoolean(KEY_YOUTUBE_283_MIGRATED, true)\n                .putBoolean(KEY_GLOBOPLAY_TELEJOURNALS_284_MIGRATED, true)',
    '.putBoolean(KEY_YOUTUBE_283_MIGRATED, true)\n                .putBoolean(KEY_YOUTUBE_412_MIGRATED, true)\n                .putBoolean(KEY_GLOBOPLAY_TELEJOURNALS_284_MIGRATED, true)',
)

worker = "app/src/main/java/br/com/monitordenoticias/android/VideoMonitorWorker.kt"
replace(
    worker,
    '''                if (!prefs.getBoolean(VideoViewModel.KEY_YOUTUBE_283_MIGRATED, false)) {
                    selected = selected + VideoSourceCatalog.youtubeOfficialIds
                    editor.putBoolean(VideoViewModel.KEY_YOUTUBE_283_MIGRATED, true)
                    changed = true
                }''',
    '''                if (!prefs.getBoolean(VideoViewModel.KEY_YOUTUBE_283_MIGRATED, false)) {
                    selected = selected + VideoSourceCatalog.youtubeOfficialIds
                    editor.putBoolean(VideoViewModel.KEY_YOUTUBE_283_MIGRATED, true)
                    changed = true
                }
                if (!prefs.getBoolean(VideoViewModel.KEY_YOUTUBE_412_MIGRATED, false)) {
                    selected = selected + setOf("youtube-g1", "youtube-domingo-espetacular")
                    editor.putBoolean(VideoViewModel.KEY_YOUTUBE_412_MIGRATED, true)
                    changed = true
                }''',
)
replace(
    worker,
    '.putBoolean(VideoViewModel.KEY_YOUTUBE_283_MIGRATED, true)\n                        .putBoolean(VideoViewModel.KEY_GLOBOPLAY_TELEJOURNALS_284_MIGRATED, true)',
    '.putBoolean(VideoViewModel.KEY_YOUTUBE_283_MIGRATED, true)\n                        .putBoolean(VideoViewModel.KEY_YOUTUBE_412_MIGRATED, true)\n                        .putBoolean(VideoViewModel.KEY_GLOBOPLAY_TELEJOURNALS_284_MIGRATED, true)',
)

print("v4.1.2 YouTube patch applied")
