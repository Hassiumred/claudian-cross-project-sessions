# Cross-project sessions for Claudian

From a chat in Project A, ask “Start a fresh session in Project B using Sonnet and ask it to review the outline.” This unofficial patch extends Claudian’s existing session tools so they can list destination Projects and select one before delivering the first message. Omitting the destination keeps the usual project inheritance. It uses the existing messaging integration and model picker.

## Compatibility

This release targets the official Claudian **2.3.47** desktop bundle. The script checks the plugin ID, version and original bundle SHA-256 before applying changes. Local verification covered Windows, project routing with a simulated host, repeated application, and byte-for-byte restoration. A full interactive handoff in Obsidian is still awaiting confirmation. The upstream feature request is [YishenTu/claudian#2276](https://github.com/YishenTu/claudian/issues/2276).

## Install

1. Install Claudian 2.3.47 and configure your Projects in Obsidian. Install Python 3.8+ and Node.js with `node` on your PATH.
2. Download and extract this repository using **Code → Download ZIP**. Close Obsidian, then open a terminal in the extracted folder containing `patch.py`.
3. Run the command below, replacing the example path with the installed plugin directory inside your vault. On macOS or Linux use `python3` and the corresponding path.

```sh
python -I patch.py --plugin-dir "C:/path/to/vault/.obsidian/plugins/realclaudian"
```

4. Reopen Obsidian and start a fresh chat. Ask it to create a session in another Project and send a short message. Open the new session in the destination Project’s history to read or continue the conversation.

## Restore or upgrade

The script saves the original `main.js` alongside the installed file as `main.js.<sha256>.bak`. Keep that backup. To restore, close Obsidian, use the same command with `--restore`, then reopen Obsidian.

```sh
python -I patch.py --plugin-dir "C:/path/to/vault/.obsidian/plugins/realclaudian" --restore
```

An official Claudian update can replace `main.js`. Check the compatibility section before applying the patch again. A version or checksum mismatch stops the script before it modifies the bundle.

## License

Distributed under the [MIT License](LICENSE). The patch includes matching fragments from Claudian by Yishen Tu.
