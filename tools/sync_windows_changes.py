#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "source")


def replace(path: str, old: str, new: str, count: int = 1):
    file = root / path
    text = file.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"sync guard failed: {path}: expected fragment not found: {old[:120]!r}")
    updated = text.replace(old, new, count)
    file.write_text(updated, encoding="utf-8")


# v4.1.1 is a non-destructive Android synchronization of the final Windows rules.
replace(
    "app/build.gradle.kts",
    'versionCode = 410\n        versionName = "4.1.0"',
    'versionCode = 411\n        versionName = "4.1.1"',
)

# News terms: force a DB upgrade so existing installations receive the missing final terms.
replace(
    "app/src/main/java/br/com/monitordenoticias/android/NewsDb.kt",
    'class NewsDb(context: Context) : SQLiteOpenHelper(context, "news.db", null, 4)',
    'class NewsDb(context: Context) : SQLiteOpenHelper(context, "news.db", null, 5)',
)
replace(
    "app/src/main/java/br/com/monitordenoticias/android/NewsDb.kt",
    '''        if (oldVersion < 4) {
            // v4.1.0: acrescenta o novo pacote de termos sem apagar nem substituir
            // nenhum termo que já exista no banco do usuário.
            insertDefaultTerms(db)
        }
    }''',
    '''        if (oldVersion < 4) {
            // v4.1.0: acrescenta o novo pacote de termos sem apagar nem substituir
            // nenhum termo que já exista no banco do usuário.
            insertDefaultTerms(db)
        }
        if (oldVersion < 5) {
            // v4.1.1: sincroniza os termos finais usados no Windows sem apagar
            // termos adicionados ou removidos pelo usuário.
            insertDefaultTerms(db)
        }
    }''',
)
replace(
    "app/src/main/java/br/com/monitordenoticias/android/NewsDb.kt",
    '''            "Maior navio da América Latina",
            "PROSUB"
        )''',
    '''            "Maior navio da América Latina",
            "PROSUB",
            "STM",
            "FORÇA AÉREA BRASILEIRA",
            "FORÇAS ARMADAS",
            "MANCHAS DE ÓLEO",
            "MILITARES",
            "MILITAR",
            "ENGEPRON"
        )''',
)

# Video terms are stored separately in SharedPreferences. A new one-shot migration
# is required because devices that already ran 4.1.0 have the old migration flag set.
video_terms_path = "app/src/main/java/br/com/monitordenoticias/android/VideoTermStore.kt"
replace(
    video_terms_path,
    '    private const val KEY_V410_BASELINE_ADDED = "video_terms_v410_baseline_added"',
    '    private const val KEY_V410_BASELINE_ADDED = "video_terms_v410_baseline_added"\n    private const val KEY_WINDOWS_SYNC_TERMS_ADDED = "video_terms_v411_windows_sync_added"',
)
replace(
    video_terms_path,
    '            val seed = clean(seedTerms + V410_BASELINE_TERMS)',
    '            val seed = clean(seedTerms + V410_BASELINE_TERMS + WINDOWS_SYNC_EXTRA_TERMS)',
)
replace(
    video_terms_path,
    '''                .putBoolean(KEY_V410_BASELINE_ADDED, true)
                .apply()''',
    '''                .putBoolean(KEY_V410_BASELINE_ADDED, true)
                .putBoolean(KEY_WINDOWS_SYNC_TERMS_ADDED, true)
                .apply()''',
    1,
)
replace(
    video_terms_path,
    '''        val current = clean(prefs.getStringSet(KEY_TERMS, emptySet()).orEmpty().toList())
        if (!prefs.getBoolean(KEY_V410_BASELINE_ADDED, false)) {
            val migrated = clean(current + V410_BASELINE_TERMS)
            prefs.edit()
                .putStringSet(KEY_TERMS, migrated.toSet())
                .putBoolean(KEY_INITIALIZED, true)
                .putBoolean(KEY_V410_BASELINE_ADDED, true)
                .apply()
            return migrated
        }
        return current''',
    '''        val current = clean(prefs.getStringSet(KEY_TERMS, emptySet()).orEmpty().toList())
        var migrated = current
        val needsV410 = !prefs.getBoolean(KEY_V410_BASELINE_ADDED, false)
        val needsWindowsSync = !prefs.getBoolean(KEY_WINDOWS_SYNC_TERMS_ADDED, false)
        if (needsV410) migrated = clean(migrated + V410_BASELINE_TERMS)
        if (needsWindowsSync) migrated = clean(migrated + WINDOWS_SYNC_EXTRA_TERMS)
        if (needsV410 || needsWindowsSync) {
            prefs.edit()
                .putStringSet(KEY_TERMS, migrated.toSet())
                .putBoolean(KEY_INITIALIZED, true)
                .putBoolean(KEY_V410_BASELINE_ADDED, true)
                .putBoolean(KEY_WINDOWS_SYNC_TERMS_ADDED, true)
                .apply()
        }
        return migrated''',
)
# The save path must also mark the new baseline as applied after manual edits.
replace(
    video_terms_path,
    '''            .putBoolean(KEY_V410_BASELINE_ADDED, true)
            .apply()''',
    '''            .putBoolean(KEY_V410_BASELINE_ADDED, true)
            .putBoolean(KEY_WINDOWS_SYNC_TERMS_ADDED, true)
            .apply()''',
    1,
)
replace(
    video_terms_path,
    '''        "Maior navio da América Latina",
        "PROSUB"
    )
}''',
    '''        "Maior navio da América Latina",
        "PROSUB"
    )

    val WINDOWS_SYNC_EXTRA_TERMS = listOf(
        "STM",
        "FORÇA AÉREA BRASILEIRA",
        "FORÇAS ARMADAS",
        "MANCHAS DE ÓLEO",
        "MILITARES",
        "MILITAR",
        "ENGEPRON"
    )
}''',
)

# Specialized sources added/refined in the Windows build.
source_path = "app/src/main/java/br/com/monitordenoticias/android/SourceCatalog.kt"
replace(
    source_path,
    '''    val specialized = listOf(
        specialized("especializada-defesa-em-foco", "Defesa em Foco", "DefesaEmFoco", "defesaemfoco.com.br"),''',
    '''    val specialized = listOf(
        specialized("especializada-defesa-em-foco", "Defesa em Foco", "DefesaEmFoco", "defesaemfoco.com.br"),
        specialized("especializada-poder-aereo", "Poder Aéreo", "Poder Aereo", "aereo.jor.br"),
        specialized("especializada-gbn-news", "GBN News", "GBN Defense", "GBNNews", "gbnnews.com.br"),''',
)
replace(
    source_path,
    'specialized("especializada-tecnodefesa", "Tecnologia & Defesa", "Tecnodefesa", "Tecnologia e Defesa", "tecnodefesa.com.br")',
    'specialized("especializada-tecnodefesa", "Tecnodefesa", "Tecnologia & Defesa", "Tecnologia e Defesa", "tecnodefesa.com.br")',
)

# The final Windows catalog used up to five major outlets per UF. The existing Android
# catalog has four per UF; append a fifth state-specific source without changing IDs or
# selections already stored. São Paulo receives A Tribuna, explicitly requested.
fifth_state_sources = '''
        ,state("AC", "Acre", "Norte", "G1 Acre", "G1 AC", "g1.globo.com/ac/acre")
        ,state("AP", "Amapá", "Norte", "G1 Amapá", "G1 AP", "g1.globo.com/ap/amapa")
        ,state("AM", "Amazonas", "Norte", "G1 Amazonas", "G1 AM", "g1.globo.com/am/amazonas")
        ,state("PA", "Pará", "Norte", "G1 Pará", "G1 PA", "g1.globo.com/pa/para")
        ,state("RO", "Rondônia", "Norte", "G1 Rondônia", "G1 RO", "g1.globo.com/ro/rondonia")
        ,state("RR", "Roraima", "Norte", "G1 Roraima", "G1 RR", "g1.globo.com/rr/roraima")
        ,state("TO", "Tocantins", "Norte", "G1 Tocantins", "G1 TO", "g1.globo.com/to/tocantins")
        ,state("AL", "Alagoas", "Nordeste", "G1 Alagoas", "G1 AL", "g1.globo.com/al/alagoas")
        ,state("BA", "Bahia", "Nordeste", "G1 Bahia", "G1 BA", "g1.globo.com/ba/bahia")
        ,state("CE", "Ceará", "Nordeste", "G1 Ceará", "G1 CE", "g1.globo.com/ce/ceara")
        ,state("MA", "Maranhão", "Nordeste", "G1 Maranhão", "G1 MA", "g1.globo.com/ma/maranhao")
        ,state("PB", "Paraíba", "Nordeste", "G1 Paraíba", "G1 PB", "g1.globo.com/pb/paraiba")
        ,state("PE", "Pernambuco", "Nordeste", "G1 Pernambuco", "G1 PE", "g1.globo.com/pe/pernambuco")
        ,state("PI", "Piauí", "Nordeste", "G1 Piauí", "G1 PI", "g1.globo.com/pi/piaui")
        ,state("RN", "Rio Grande do Norte", "Nordeste", "G1 Rio Grande do Norte", "G1 RN", "g1.globo.com/rn/rio-grande-do-norte")
        ,state("SE", "Sergipe", "Nordeste", "G1 Sergipe", "G1 SE", "g1.globo.com/se/sergipe")
        ,state("DF", "Distrito Federal", "Centro-Oeste", "G1 Distrito Federal", "G1 DF", "g1.globo.com/df/distrito-federal")
        ,state("GO", "Goiás", "Centro-Oeste", "G1 Goiás", "G1 GO", "g1.globo.com/go/goias")
        ,state("MT", "Mato Grosso", "Centro-Oeste", "G1 Mato Grosso", "G1 MT", "g1.globo.com/mt/mato-grosso")
        ,state("MS", "Mato Grosso do Sul", "Centro-Oeste", "G1 Mato Grosso do Sul", "G1 MS", "g1.globo.com/ms/mato-grosso-do-sul")
        ,state("ES", "Espírito Santo", "Sudeste", "G1 Espírito Santo", "G1 ES", "g1.globo.com/es/espirito-santo")
        ,state("MG", "Minas Gerais", "Sudeste", "G1 Minas Gerais", "G1 MG", "g1.globo.com/mg/minas-gerais")
        ,state("RJ", "Rio de Janeiro", "Sudeste", "G1 Rio de Janeiro", "G1 RJ", "g1.globo.com/rj/rio-de-janeiro")
        ,state("SP", "São Paulo", "Sudeste", "A Tribuna", "A Tribuna de Santos", "atribuna.com.br")
        ,state("PR", "Paraná", "Sul", "G1 Paraná", "G1 PR", "g1.globo.com/pr/parana")
        ,state("SC", "Santa Catarina", "Sul", "G1 Santa Catarina", "G1 SC", "g1.globo.com/sc/santa-catarina")
        ,state("RS", "Rio Grande do Sul", "Sul", "G1 Rio Grande do Sul", "G1 RS", "g1.globo.com/rs/rio-grande-do-sul")'''
replace(
    source_path,
    '''        state("RS", "Rio Grande do Sul", "Sul", "Sul21")
    )''',
    '''        state("RS", "Rio Grande do Sul", "Sul", "Sul21")''' + fifth_state_sources + '''
    )''',
)

# Direct latest-news collector routes for the two new specialized outlets.
latest_path = "app/src/main/java/br/com/monitordenoticias/android/NewsLatestCollector.kt"
replace(
    latest_path,
    '''            "especializada-defesa-aerea-naval" to Route("https://www.defesaaereanaval.com.br/", setOf("defesaaereanaval.com.br")),''',
    '''            "especializada-defesa-aerea-naval" to Route("https://www.defesaaereanaval.com.br/", setOf("defesaaereanaval.com.br")),
            "especializada-poder-aereo" to Route("https://www.aereo.jor.br/", setOf("aereo.jor.br")),
            "especializada-gbn-news" to Route("https://www.gbnnews.com.br/", setOf("gbnnews.com.br")),''',
)

# g1 official YouTube channel. The helper intentionally targets the channel /videos tab.
video_sources_path = "app/src/main/java/br/com/monitordenoticias/android/VideoSourceCatalog.kt"
replace(
    video_sources_path,
    '''    val youtubeOfficial = listOf(
        youtube("youtube-cnn-brasil", "CNN Brasil", "@CNNBrasil", listOf("CNN", "CNN Brasil")),''',
    '''    val youtubeOfficial = listOf(
        youtube("youtube-cnn-brasil", "CNN Brasil", "@CNNBrasil", listOf("CNN", "CNN Brasil")),
        youtube("youtube-g1", "g1", "@g1", listOf("g1", "G1 Notícias", "G1 Jornalismo")),''',
)

print("Windows -> Android synchronization patch applied successfully")
