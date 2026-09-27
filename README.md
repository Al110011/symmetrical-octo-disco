# Mon premier dépôt
Ceci est un test pour créer mon premier fichier sur GitHub.
                                                

## Vidéo (HyperFrames)

Le dossier `video/` contient un projet [HyperFrames](https://github.com/heygen-com/hyperframes) : une composition HTML (`video/index.html`) rendue en vidéo MP4 (1920×1080, paysage) : le clip `video/assets/clip-solar.mp4` avec le titre « Zaragoza Spain solar eclipse » pendant les 3 premières secondes.

La vidéo source n'est pas versionnée (`assets/` et `renders/` sont dans `.gitignore`) : copie ton clip sous `video/assets/clip-solar.mp4` avant l'aperçu ou le rendu.

```bash
cd video
npm run dev     # aperçu dans le navigateur
npm run check   # validation de la composition
npm run render  # rendu MP4 (nécessite Chrome et FFmpeg)
```
