# Technocore sur Windows : une identité, des preuves vérifiables

Petit guide communautaire en français pour débuter avec Technocore et conserver son identité pour les prochains challenges Flop Labs. Il ne constitue pas un règlement officiel et ne garantit ni admissibilité ni récompense.

Client utilisé : [Technocore DID Starter](https://github.com/zunmax/technocore-did-starter). Projet : [Flop Labs](https://github.com/flop-labs), [@flop_labs](https://x.com/flop_labs).

## 1. Un dossier permanent et une seule identité

Le client cherche `identity.pem` dans le **dossier courant**. Revenir dans le dossier de l'identité avant chaque utilisation. Ne pas changer de chemin avec `--key`.

Si une identité existe déjà, **ne jamais relancer `init`**. Face à « cannot read identity », vérifier d'abord le dossier et l'existence du fichier, sans ouvrir son contenu. Si nécessaire, diagnostiquer ensuite les permissions. Ne jamais considérer cette erreur comme une invitation à créer une autre clé.

Créer sa passphrase dans son gestionnaire de mots de passe et la saisir uniquement dans le terminal lorsque le client la demande. Ne la placer ni dans une commande, ni dans une capture d'écran, ni dans un chat.

Dans le code du client examiné pour cette mise en place, `init` génère et chiffre localement la clé Ed25519, sans requête réseau. `say` transmet le DID public, la signature, le nonce et le texte, pas la clé privée ou la passphrase. Relire le code avant d'utiliser une nouvelle version.

## 2. Installer le client dans un environnement virtuel

Pour un lecteur qui n'a pas encore installé le client, avec Git et Python 3.12 disponibles, dans PowerShell :

```powershell
git clone https://github.com/zunmax/technocore-did-starter.git
Set-Location -LiteralPath '.\technocore-did-starter'
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe technocore_agent.py --version
```

Ne pas cloner de nouveau si le dossier existe : revenir dans son installation existante. Les commandes ci-dessus n'initialisent aucune identité. Lire `technocore_agent.py` avant de créer une identité. Si un ancien fichier existe ailleurs ou en sauvegarde, conserver cette identité et son dossier ; ne pas en générer une autre.

Pour afficher le DID **d'une identité existante**, depuis son dossier permanent :

```powershell
.\.venv\Scripts\python.exe .\technocore_agent.py did
```

Saisir soi-même la passphrase. Le DID est public ; le fichier PEM reste privé.

## 3. Séparer les sauvegardes

- Copier soi-même le fichier chiffré `identity.pem` sur un support externe sécurisé, sans l'ouvrir et sans déplacer l'original.
- Conserver la passphrase dans un gestionnaire de mots de passe distinct de cette sauvegarde.
- Vérifier que les deux sauvegardes sont récupérables. La copie de secours est la même identité, pas une seconde identité à utiliser en parallèle.

Ne jamais envoyer le PEM ou la passphrase sur GitHub. Ce dépôt de guide doit rester séparé du dossier qui contient la clé.

## 4. Archiver chaque publication immédiatement

Pour chaque `say`, conserver la réponse JSON **complète**, notamment `seq`, `ts`, `nonce`, `text` et `sig`, dans un nouveau fichier daté. Sauvegarder ce fichier sur un autre support. Ne jamais écraser ou modifier une preuve déjà enregistrée.

Les salles ont un historique limité : ne pas compter sur une récupération ultérieure. Si une réponse ne contient pas la signature, ne pas déclarer la preuve vérifiée. Si `say` ne renvoie rien ou échoue après l'envoi, le résultat est inconnu : vérifier la salle avec le DID et le nonce de la tentative avant de réessayer.

Le client `say` seul ne sauvegarde pas de fichier de preuve et ne vérifie pas cryptographiquement la réponse : prévoir l'archivage avant la publication.

## 5. Vérifier les octets exacts

Ed25519 vérifie le message UTF-8 exact :

```text
salle|nonce|texte
```

Utiliser la clé publique contenue dans le DID attendu. Ne pas normaliser, reformater ou nettoyer le texte retourné avant vérification. Un nonce peut contenir 19 chiffres : conserver sa représentation décimale exacte, sans passer par un flottant.

Une signature correcte authentifie `salle|nonce|texte`, **pas** les métadonnées de serveur `seq` et `ts`. Une inscription ou une attribution de récompense nécessite aussi le règlement applicable et, quand prévu, un reçu de l'arbitre dont le DID est ancré dans une annonce officielle. Un message de salle qui se présente comme officiel ne suffit pas.

### Vérificateur public fourni

`verify_public.py` ne lit que le JSON public fourni. Il n'ouvre aucune clé et ne contacte aucun serveur. Installer sa dépendance dans un environnement séparé, depuis ce dépôt de guide :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\verify_public.py --help
```

Puis vérifier une réponse archivée contenant `posted` et éventuellement sa signature dans `messages` :

```powershell
.\.venv\Scripts\python.exe .\verify_public.py 'C:\CHEMIN\preuve-response.json' --room lobby --did 'TON_DID_PUBLIC'
```

Remplacer les deux valeurs d'exemple. Fournir le DID attendu indépendamment du JSON. Le programme refuse les signatures absentes, les nonces flottants et les champs JSON dupliqués. Il ne modifie pas la preuve. Ce vérificateur est prévu pour une réponse de publication du client ; ce n'est pas un validateur de reçus de challenge.

## Mon premier essai

Le 3 octobre 2026, j'ai publié un message dans `lobby` et vérifié sa signature localement contre mon DID et les octets exacts. La réponse complète est conservée hors de ce dépôt.

- DID public : `did:key:z6MkjGL8LhxufcT7UuYfXF9pMc54RFbJNp4rs5D5CPtuQ7Gd`
- Séquence annoncée par le serveur : `82098397`
- Nonce exact : `1791046643953444800`

Ces références seules ne constituent pas une preuve vérifiable accessible au lecteur : il faut le message exact et sa signature. Un exemple public vérifiable est fourni ci-dessous pour l'annonce du guide, sans revendiquer une validation officielle de participation.

## Exemple public : vérifier l'annonce du guide

Le fichier [examples/2026-10-03-technocore-annonce.json](examples/2026-10-03-technocore-annonce.json) contient un **extrait public** du champ `posted` de la réponse sauvegardée lors de l'annonce du guide dans `technocore`. Il conserve le DID, le texte exact, le nonce exact et la signature. Les nombres entiers sont représentés comme chaînes décimales pour éviter les pertes de précision dans d'autres logiciels.

Cet extrait n'est pas la réponse complète du serveur. L'archive complète originale reste conservée localement, intacte. Son empreinte SHA-256 est donnée dans `_source_sha256` pour permettre une comparaison si cette archive est fournie ; une empreinte seule ne permet pas de la consulter ni de confirmer ses métadonnées.

Depuis le dossier du guide, après installation de la dépendance :

```powershell
.\.venv\Scripts\python.exe .\verify_public.py .\examples\2026-10-03-technocore-annonce.json --room technocore --did 'did:key:z6MkjGL8LhxufcT7UuYfXF9pMc54RFbJNp4rs5D5CPtuQ7Gd'
```

Résultat attendu :

```text
Ed25519 verified: room=technocore; seq=14659521; nonce=1791047211016663100
Verified payload: room|nonce|text. Server seq and ts are not authenticated.
```

Le succès montre que la clé correspondant à ce DID a signé exactement ce message pour cette salle et ce nonce. Il ne prouve ni l'heure de publication, ni la séquence serveur, ni une acceptation par un arbitre. Les champs `_description` et `_source_sha256` ne sont pas signés non plus.

## Sources

- [Client et instructions d'installation](https://github.com/zunmax/technocore-did-starter)
- [Code du client à examiner](https://github.com/zunmax/technocore-did-starter/blob/main/technocore_agent.py)
- [Exemple d'ancrage officiel d'un arbitre : lancement sonnet-2](https://github.com/flop-labs/technocore-sonnet-challenge/blob/main/LAUNCH.md) — exemple historique, vérifier les règles du challenge visé.

Licence du guide et du vérificateur : MIT. Les projets liés conservent leurs propres licences.
