# Frontend

[![English](https://img.shields.io/badge/lang-English-lightgrey)](../en/FRONT.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-blue)](FRONT.md)

Application monopage écrite en React 19 et TypeScript (mode strict), construite avec Vite.

| Besoin | Choix | Pourquoi |
|---|---|---|
| Routage | React Router | Standard de fait, pages pilotées par l'URL |
| Données serveur | TanStack Query | Cache, rafraîchissement et invalidation sans état écrit à la main |
| Style | CSS simple avec variables | Petite application, pas besoin de framework ; un thème clair |
| Lint / formatage | oxlint, Prettier | Lint rapide, formatage homogène |
| Tests | Vitest, Testing Library, MSW | Les tests utilisent l'application comme un utilisateur, face à une fausse API HTTP |

## Architecture

```
frontend/src/
├── api/          # Client HTTP, une fonction par endpoint, types des réponses
├── auth/         # Hooks de session (utilisateur courant, connexion, déconnexion), redirections sûres
├── components/   # Mise en page, formulaire de vote, graphique des résultats, garde d'accès, messages
├── pages/        # Un composant par route
├── test/         # Configuration des tests, fausse API (MSW), données de test, helper de rendu
└── AppRoutes.tsx # Table des routes
```

Les composants n'appellent jamais `fetch` directement : ils utilisent des hooks TanStack Query,
qui appellent les fonctions de `src/api/`. Toutes les données serveur vivent dans le cache des
requêtes ; il n'y a pas de store global.

| Route | Page | Accès |
|---|---|---|
| `/` | Liste des sondages | public |
| `/polls/:id` | Sondage, formulaire de vote et résultats en direct | public, voter demande d'être connecté |
| `/polls/new` | Création d'un sondage | connecté (sinon redirection vers la connexion) |
| `/login`, `/register` | Authentification | public |

## Communication avec l'API

Le navigateur ne parle qu'à **une seule origine**. Les requêtes partent vers des chemins
relatifs (`/api/v1/...`) et sont routées vers le backend par :

| Environnement | Routeur |
|---|---|
| Développement (`npm run dev`) | Proxy du serveur de dev Vite (`vite.config.ts`) |
| Docker Compose | nginx qui sert le frontend |
| Kubernetes | Ingress (`/api` → backend, `/` → frontend) |

Conséquences :

- **Aucune configuration CORS** n'est nécessaire.
- Le **cookie de session** (`HttpOnly`, `SameSite=Lax`) est envoyé automatiquement. Le frontend
  ne voit et ne stocke jamais de token : une attaque XSS n'a rien à voler.
- Le **même build** tourne dans tous les environnements : l'URL de l'API n'est pas figée dans le
  bundle, donc une seule image est promue de staging à production.

Le client API (`src/api/client.ts`) transforme les réponses en erreur en `ApiError`, avec le
statut HTTP et le message de l'API, que les pages affichent tel quel.

## Expérience utilisateur

- `has_voted`, renvoyé par l'API, remplace le formulaire de vote par une confirmation ; un second
  vote est impossible depuis l'interface, et de toute façon refusé par l'API (`409`).
- Les résultats sont rafraîchis toutes les 5 secondes tant qu'un sondage est affiché.
- Après connexion, l'utilisateur revient sur la page d'où il venait (`?next=`). Seuls les chemins
  locaux sont acceptés, pour éviter les redirections ouvertes (open redirect).
- La validation reprend les règles de l'API (2 à 10 options uniques, mot de passe ≥ 12
  caractères) pour un retour immédiat ; l'API reste la source de vérité.
- Accessibilité : champs étiquetés, `role="alert"` pour les erreurs, `role="meter"` pour les
  barres de résultats, focus visible, préférence « mouvements réduits » respectée.

## Développement

```bash
cd frontend
npm ci
npm run dev            # http://localhost:5173, redirige /api vers http://localhost:8000
```

Le backend doit tourner (voir [BACK.md](BACK.md)). Une autre adresse d'API peut être utilisée
avec `VOTELY_API_URL=http://hote:port npm run dev`.

| Commande | Rôle |
|---|---|
| `npm run build` | Vérification des types et build dans `dist/` |
| `npm run typecheck` | TypeScript seul |
| `npm run lint` | oxlint (les avertissements font échouer la commande) |
| `npm run format` / `format:check` | Prettier |
| `npm test` / `test:watch` | Vitest |
| `npm run test:coverage` | Tests avec couverture (minimum 80 % des lignes) |

## Tests

Les tests affichent toute l'application à une URL donnée (`renderApp('/polls/42')`) et
l'utilisent comme le ferait un utilisateur : par rôles et libellés, en tapant et en cliquant.

L'API est remplacée par [MSW](https://mswjs.io/) (`src/test/server.ts`), qui intercepte les
vrais appels `fetch`. La fausse API garde un petit état (comptes, session, votes) : des parcours
comme « s'inscrire puis voir son email dans l'en-tête » ou « voter puis voir la confirmation »
sont testés de bout en bout côté frontend. Toute requête sans handler fait échouer le test.

Ce qui est couvert :

- Client API : succès, `204`, messages d'erreur, erreurs de validation, erreurs non JSON.
- Pages : liste des sondages (état vide, badges, erreurs), détail (résultats, 404), création
  (garde d'accès, options dynamiques, doublons), connexion / inscription / déconnexion,
  redirections sûres.
- Formulaire de vote : visiteur anonyme, vote réussi, déjà voté, sondage fermé, vote refusé.

Les tests dans un vrai navigateur face au vrai backend arrivent avec la suite end-to-end (voir
TESTS.md).

## Limites connues

- Un visiteur anonyme déclenche un `401` sur `GET /api/v1/auth/me`, que les navigateurs affichent
  dans la console. C'est la réponse attendue (« non connecté »), gérée par l'application.
- Les résultats sont rafraîchis par polling, pas par WebSockets : simple et suffisant pour ce
  trafic.
