# 📋 GUIDE D'ACCÈS POUR LES AUTRES PCs

## ✅ Ce que vous avez BESOIN :
- Un navigateur web (Chrome, Firefox, Edge, Safari)
- Être connecté au **réseau local** de l'institut
- C'est TOUT !

---

## 🌐 COMMENT ACCÉDER À L'APPLICATION

### URL à utiliser :
```
http://192.168.42.39:8000/
```

### Ou le nom si disponible sur le réseau :
```
http://pc-serveur:8000/
```
(Demandez à l'admin le nom du PC serveur)

---

## ⚠️ CONDITIONS IMPORTANTES

1. **Le PC serveur (celui avec le label sur le bureau) DOIT être allumé**
   - C'est sur ce PC que tournent les bases de données et l'application
   - Si c'est éteint, l'application n'est pas accessible

2. **Les deux doivent être sur le MÊME réseau local**
   - Pas de VPN nécessaire si vous êtes physiquement au même endroit
   - Si vous êtes à distance, demandez à l'admin de configurer un accès VPN

3. **La première fois, acceptez les certificats de sécurité si demandé**

---

## 🔐 IDENTIFIANTS DE CONNEXION

Demandez-les auprès de l'administrateur de l'application (actuellement : Yanis ou la direction)

---

## 🆘 DÉPANNAGE

### "Impossible de se connecter" / "Serveur non trouvé"
- ✅ Vérifiez que le PC serveur est allumé
- ✅ Vérifiez que vous êtes connecté au même réseau WiFi/Ethernet
- ✅ Essayez de ping le serveur : ouvrez CMD et tapez : `ping 192.168.42.39`

### "La page se charge très lentement"
- C'est normal sur un réseau local si beaucoup de monde utilise l'app
- Essayez un autre navigateur
- Attendez quelques secondes

### "Erreur 500 / Page blanche"
- Redémarrez l'application (fermerez et relancez le script START_SERVER.bat sur le PC serveur)
- Videz le cache du navigateur : Ctrl+Shift+Delete

---

## 📧 SUPPORT

Contactez l'administrateur système :
- **Téléphone** : [à définir]
- **Email** : [à définir]

---

**Dernière mise à jour** : 25 Décembre 2025
**Version** : 1.0
