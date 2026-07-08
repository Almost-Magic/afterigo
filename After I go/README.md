# After I Go

After I Go is a private browser vault for practical end-of-life planning. It helps someone organise messages, wishes, trusted contacts, important documents, accounts, and exportable notes for the people who may need them later.

## What this is

This is a planning and organisation tool. It is not legal advice, financial advice, medical advice, therapy, crisis care, emergency support, estate planning advice, or a replacement for a will, power of attorney, advance care directive, executor, lawyer, accountant, doctor, or trusted human conversation.

## Who it helps

- someone who wants to leave clearer notes for loved ones;
- a family member helping organise practical details;
- a carer or trusted person preparing a handoff document;
- an open-source contributor who wants to improve local-first planning tools.

## What you can do now

- write messages and wishes;
- map important accounts and documents;
- name trusted people;
- review security and sharing settings;
- export a local handoff packet where the app supports it.

## Safety boundaries

- Do not rely on the app as the only copy of critical instructions.
- Do not store secrets unless you understand the local storage and export model.
- Confirm legal, financial, medical, funeral, and estate decisions with qualified people.
- If someone is in immediate danger, contact emergency services now.

## Run locally

```bash
npm install
npm run dev
```

Then open the local URL shown by Vite.

## Checks

```bash
npm test
npm run build
```

## Public repo warning

The public `afterigo` repository currently contains a broad AMTL/Elaine workspace plus this nested `After I go` app. For a clean open-source release, create or confirm a dedicated product repo, move this app to the repo root, and put the licence file at the public repo root.

## Good first issues

- add a plain-language export verification guide;
- add tests for export, import, and failure paths;
- document exactly what is stored locally;
- improve mobile setup flow screenshots;
- add a checklist for legal and professional review wording.

## Licence

The nested app package declares MIT. See [LICENSE](LICENSE).
