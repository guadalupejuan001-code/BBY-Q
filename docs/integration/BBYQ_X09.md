# BBY-Q X09

X09 connects the original complete E031 dictionary and the alternative E009
campaign to the X08 conversational agent, with one persisted RVPC2 state per
session. XI recognizes requests, selects dictionary records, reasons over the
campaigns, and runs the inherited Qd/w4U roles. Node handles bytes, file integrity,
native process invocation, and session publication.

## Run from a checkout

Requires Linux x86-64, Node.js 24+, `unzip`, `tar`, and `flock`, plus the recovered
`BBY-Q-X09-Entrenamientos-Integrados.zip` kept locally.

```sh
node bbyq.mjs prepare --archive /path/BBY-Q-X09-Entrenamientos-Integrados.zip
node bbyq.mjs init /tmp/bbyq-session
node bbyq.mjs turn /tmp/bbyq-session request-1 --language=en '@lex money'
node bbyq.mjs turn /tmp/bbyq-session request-2 'edificio incluye libro?'
```

`prepare` verifies the original archive hash and all native asset hashes, then
restores its data locally without a network download.
Its default output is `build/x09`. Use `--build DIRECTORY` before other commands
to choose another restored build. Existing builds and sessions are preserved.
Retry an uncertain turn with the same request ID and the same text and language;
the saved receipt prevents a second state update.

To update an X08 session without replacing its original version:

```sh
node bbyq.mjs migrate-session /path/to/x08-session migrate-x09-1
```

## Included data and compatibility

- E031: 236,256 original entries, 88,950 Spanish and 147,306 English.
- Both E009 campaigns: the primary bank remains intact; the alternative uses
  distinct concept IDs and a separate logical region.
- X08: the original canonical training state, Babilonia, document context, and
  inherited programming roles remain available.
- The canonical X09 model SHA-256 is
  `71ba9704e279c08160a8af882a8628b77e938a30befa450e95a522315a39f995`.
- The recovered archive contains a canonical educational fixture. Personal
  sessions and generated conversations are never packaged by the exporter.
- The restored executable is the exact Linux runtime from the recovered X09
  archive. Native file, corpus, and runtime hashes are verified before use.
- This code integration keeps the X09 corpus, native binaries, and the five
  historical training payloads in local inputs. They are not new public Git files.

This integration does not establish unrestricted language understanding. Android
and the REVERSE APK require separate integration and device validation. P13/P14
remain excluded as in the X08 dependency.

## Verification

```sh
node integration/x09/check.mjs /tmp/bbyq-x09-verification /path/BBY-Q-X09-Entrenamientos-Integrados.zip /path/historical-states
```

The check restores a fresh release, recompiles the six XI extension roles from
the checked-in source and compares their binary hashes, reconstructs the exact
X09 model from X08, runs chat and programming tasks, checks dictionary corruption
and campaign isolation, and audits all 22 frozen historical payloads. The 17
repository checkpoints are read directly from the checkout. The five earlier
synthetic training states come from the supplied local directory, under their
original filenames and frozen hashes; the original audit source is checked in.
It also exercises session initialization failure, imports, migration, and retries.

The full original dictionary ZIP can still be used for an independent source
rebuild with `ai/personal/x09/build.mjs`. Its pinned SHA-256 is
`70a9d7036f370f8328f22c7f29c3c9832ac7a875876f8992be03bc8e44ceb488`.
The recovered X09 ZIP contains the complete packed corpus, so running the agent
after preparation does not require the E031 export or any previous chat workspace.
Public CI runs the source, session, preparation, and 17 repository-checkpoint
checks. Full native/corpus verification uses the local inputs named above.
