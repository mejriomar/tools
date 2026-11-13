# Diagnostic USB MSC STM32N6 : échec d'écriture avec host STM32H7RS

Nov 14, 2026 · @omar

## Ce que disent les symptômes

Le device STM32N6 (USBX + ThreadX, stockage sur carte SD) fonctionne avec un PC sous les quatre environnements (EWARM, MDK-ARM, CubeIDE-debug, CubeIDE-release), mais pas avec un host STM32H7RS. Ce document liste les causes possibles ; il repose sur le code du device uniquement, le code du host n'ayant pas été vu.

- **Fichier créé mais vide (EWARM, MDK-ARM, CubeIDE-release)** : l'entrée de répertoire FAT, petite écriture, est passée, mais les données et la taille n'ont pas été écrites. Soit le host n'a pas fait `close` ou `flush`, soit l'écriture suivante a échoué ou s'est bloquée.
- **Création impossible (CubeIDE-debug)** : même l'écriture du répertoire échoue, ce qui évoque un timeout ou une erreur.
- **Résultat qui varie selon l'IDE, avec la même carte et le même host** : un bug de logique pur donnerait le même résultat partout. Cela évoque plutôt le temps de réponse (le debug est plus lent), la mémoire ou le comportement du host.

## Cause 1 : une erreur SD bloque le device sans le signaler

Dans `ux_device_msc.c`, les callbacks `HAL_SD_ErrorCallback` et `HAL_SD_AbortCallback` n'existent pas (aucune occurrence dans le projet). Si le DMA échoue (CRC, timeout), `tx_event_flags_get(..., TX_WAIT_FOREVER)` n'est jamais débloqué et le host reçoit un timeout.

Autre piste : `check_sd_status()` échoue après 100 ticks (1 s à 100 ticks/s) et appelle `Error_Handler()`, qui boucle.

- **Vérifier** : la LED rouge clignote-t-elle pendant l'échec ? Mettre un point d'arrêt dans `Error_Handler`.
- **Corriger** : ajouter les deux callbacks pour lever un flag d'erreur et débloquer le thread.

## Cause 2 : le build debug est plus lent que le host ne le tolère

Un host USBX/FileX a des timeouts plus stricts qu'un PC Windows ou Linux, qui réessaie longtemps. Côté device, `check_sd_status()` fait de l'attente active et un `HAL_Delay(10)` est appelé dans l'interruption EXTI (`app_usbx_device.c`). Un build -O0, ou avec le debugger attaché, peut dépasser le timeout du host. Cela correspond au fait que seul CubeIDE-debug échoue complètement.

- **Vérifier** : mesurer le temps passé dans `USBD_STORAGE_Write` (GPIO ou DWT), en debug et en release.
- **Vérifier aussi** : lancer CubeIDE-debug sans debugger attaché.

## Cause 3 : le comportement du host STM32H7RS

Le symptôme « fichier vide » est typique d'un host qui n'a pas vidé son cache FileX.

- **`close` et `flush`** : `fx_file_close()` ou `fx_media_flush()` est-il appelé après l'écriture ? FileX garde les données en cache.
- **D-cache du H7RS** : les tampons du host USBX et du media driver FileX doivent être dans une zone non cacheable ou nettoyés avant l'envoi, sinon le device reçoit des données périmées ou nulles.
- **exFAT** : si la carte est formatée en exFAT, FileX n'écrit que si `FX_ENABLE_EXFAT` est activé. Je n'ai vu ni la carte ni le code host.
- **Vérifier** : tester avec une carte fraîchement formatée en FAT32 (32 Go maximum) et lire les codes de retour de `fx_file_create`, `fx_file_write` et `fx_file_close`.

## Cause 4 : vitesse négociée différente (Full Speed au lieu de High Speed)

Le device configure `PCD_SPEED_HIGH` dans `usb_otg.c` et fournit deux jeux de descripteurs : paquets bulk de 512 octets en HS, de 64 octets en FS. Le PC est probablement en HS, mais le port du Nucléo H7RS peut négocier FS. En FS il y a beaucoup plus de paquets et un chemin de code différent, ce qui fait ressortir des problèmes de timing ou de FIFO.

Les tailles de FIFO sont définies dans `usb_otg.c` : Rx `0x200`, Tx0 `0x40`, Tx1 `0x100`. Elles semblent suffisantes en HS ; je n'ai pas vérifié leur dimensionnement en FS.

- **Vérifier** : la vitesse énumérée côté host (`ux_host_stack_device_get` ou le champ de vitesse de l'appareil).

## Causes 5 et 6 : mémoire et cache (peu probables), détails mineurs

**Mémoire et cache.** J'ai contrôlé les trois scripts de link : `.UsbxPoolSection` est placé à `0x341FD800` dans EWARM, MDK-ARM et CubeIDE, donc dans la région non cacheable de la MPU (`0x341FC800–0x341FFFFF`). Le DMA SD sur les tampons USBX est cohérent, ce qui explique l'absence d'invalidation de cache dans le code. Si le build CubeIDE-debug place autre chose dans cette région, ou si le pool de 7168 octets déborde, le résultat peut changer : comparer les fichiers `.map`.

**Détails mineurs.**

- `EventFlag` n'est pas remis à zéro avant chaque transfert ; un flag périmé pourrait faire repartir un thread trop tôt.
- `USBD_STORAGE_Status` ne renseigne jamais `media_status`.
- `USBD_STORAGE_Flush` est vide. L'écriture étant synchrone avec le DMA, ce n'est normalement pas bloquant.

## Plan de test

1. Observer la LED rouge pendant un échec (cause 1).
2. Ajouter dans `USBD_STORAGE_Write` un log du LBA, du nombre de blocs et de la durée ; comparer l'écriture d'un fichier entre EWARM et CubeIDE-debug.
3. Brancher le host sur le PC avec les mêmes builds, puis sur le H7RS avec la même carte formatée, pour isoler le host.
4. Dans le code host, tester les codes de retour FileX, ajouter `fx_media_flush` et vérifier la vitesse énumérée.
