# Erreur FX\_MEDIA\_NOT\_OPEN (0x11) côté host STM32H7RS

Nov 14, 2026 · @omar

## Ce que signifie 0x11

Le code `0x11` (`FX_MEDIA_NOT_OPEN`) veut dire que FileX ne considère pas le média comme ouvert au moment de l'appel. `fx_media_open` lui-même ne renvoie normalement pas cette valeur : elle vient des appels qui suivent (`fx_file_create`, `fx_file_write`, `fx_media_flush`...). Il faut donc préciser quel appel la renvoie, car cela change le diagnostic.

Cela déplace le problème : ce n'est plus l'écriture USB ou SD qui échoue, c'est que le media n'est plus ou n'a jamais été ouvert côté host. Cela s'accorde avec le symptôme « fichier créé mais vide » : la création peut réussir tant que le media est ouvert, puis il se ferme avant l'écriture.

## Cause 1 : `fx_media_open` a échoué sans que son retour soit testé

`fx_media_open` échoue si la lecture du secteur 0 échoue (`FX_MEDIA_INVALID`, `FX_FAT_READ_ERROR`, `FX_BOOT_ERROR`, `FX_IO_ERROR`...). Les appels FileX suivants renvoient alors `0x11`.

- **Vérifier** : loguer le code de retour de `fx_media_open` et le comparer à la table des codes FileX.

## Cause 2 : le device N6 se déconnecte ou se réénumère

Dans `app_usbx_device.c`, un message `STOP_USB_DEVICE` ou `STOP_SD_CARD` déclenche `ux_device_stack_disconnect()` puis `HAL_PCD_Stop()`.

- `STOP_USB_DEVICE` est envoyé par la pile USBPD (`usbpd_usb_if.c`), par exemple sur un événement de contrat de puissance ou de rôle.
- `STOP_SD_CARD` vient de l'EXTI12 sur SD\_DETECT ; un rebond sur cette broche suffit à tout arrêter.

Le host USBX voit alors un débranchement, et son code d'application ferme le media (`fx_media_close`). Le `0x11` apparaît à l'écriture suivante.

- **Vérifier côté device** : poser un point d'arrêt dans `app_ux_device_thread_entry` sur la branche d'arrêt (`HAL_PCD_Stop`).
- **Vérifier côté host** : le callback de désactivation de la classe Storage est-il appelé avant l'erreur ?

## Causes 3 et 4 : instance de media ou ordre d'initialisation côté host

**Cause 3 : media fermé ou mauvais `FX_MEDIA`.** Le media a été fermé ailleurs dans le code (thread de gestion du déconnect, code de démo), ou l'appel utilise une autre instance `FX_MEDIA` que celle ouverte. Si la structure `FX_MEDIA` est écrasée en RAM, son identifiant n'est plus valide et FileX renvoie aussi `0x11`.

**Cause 4 : ordre d'initialisation.**

- `fx_media_open` doit être appelé après que la classe Storage soit détectée et prête, avec le driver `_ux_host_class_storage_driver`. Appelé trop tôt, avant la fin de l'énumération, il échoue.
- Le tampon de secteur passé à `fx_media_open` doit être assez grand et dans une zone non cacheable sur le H7RS.

## À regarder en premier

1. Loguer les retours de `fx_media_open`, puis de chaque appel FileX suivant, avec l'instant en ticks.
2. Mettre un point d'arrêt sur `fx_media_close` côté host : si on y passe avant l'erreur, la cause est la déconnexion (cause 2).
3. Côté N6, regarder si la LED rouge clignote (`Error_Handler`) ou si le thread passe par la branche d'arrêt.

Pour resserrer le diagnostic, il faudrait le code host qui ouvre le media et celui qui écrit (`fx_media_open`, `fx_file_create`, `fx_file_write`), ainsi que le callback de la classe Storage.
