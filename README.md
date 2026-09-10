# Monitor de Notícias Android

Repositório de build Android do **Monitor de Notícias v4.0.2**.

## Fonte validada

O APK é compilado a partir do commit fixo:

`RODRIGODESS/monitor-de-noticias-apk@b131711f1f2d368a9d3dc59d6d211e9680ac7c8f`

Esse commit foi conferido contra o pacote recuperado da conversa anterior, `monitor-de-noticias-apk-windows-v4.0.2-portable.zip`. O Git tree do módulo `app/` é `d36b85ce9e60279367a14163ebe4d662006f8491`, exatamente igual no ZIP e no commit de origem.

O aplicativo é Android nativo em **Kotlin + Jetpack Compose**, com `applicationId` `br.com.monitordenoticias.android`, `versionCode` 402 e `versionName` 4.0.2.

## Como o APK é gerado

O workflow `.github/workflows/build-apk.yml`:

1. busca o commit validado do projeto original;
2. mantém apenas o módulo Android durante a compilação;
3. instala Java 17, Android SDK 35 e Gradle 8.11.1;
4. executa `:app:assembleDebug`;
5. gera `monitor-de-noticias-v4.0.2-debug.apk` e o SHA-256;
6. publica o APK como artefato do GitHub Actions e como pré-release de teste.

## Observação sobre assinatura

O APK produzido por este fluxo é uma **build DEBUG instalável**, indicada para validação no telefone. Ele não deve ser usado para substituir uma instalação assinada com uma chave de produção diferente. Uma release definitiva deve usar a chave permanente do aplicativo por meio de GitHub Actions Secrets, sem versionar o keystore.
