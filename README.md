# Java Piscine | Zone01 Athens

Complete the [13 piscine stages](PATH.md). GitHub tracks work. The Athens Platform records results from its assigned Gitea repositories, checkpoints and audits.

## Set up your workspace

1. Once staff grant board access, copy the [cohort board](https://github.com/orgs/zone01athens/projects/10) to your GitHub account. Select **Make a copy** and enable **Copy draft issues**.
2. Select **Use this template → Create a new repository**. Choose your account and set visibility to **Private** so your solutions stay private.
3. Clone your copy. Open the Maven project in IntelliJ IDEA, select JDK 17 or later, and sync Maven.
4. Run `mvn test` from the repository root. Expect `GreetingTest` to pass. Run `Greeting.main` without arguments to verify console output: `Hello, Athens!`.

## Install the Zone01 tester once

Sign in to GitHub with the account invited to the private Zone01 tester repository. In your browser, download both the archive and its checksum from the [Zone01 tester release](https://github.com/zone01athens/java-piscine-tester/releases/tag/java-tester-a0f74962). Use your existing GitHub session. No personal access token or registry login is required. Verify the archive in the download directory:

```sh
# Linux
sha256sum -c java-piscine-tester-a0f74962.tar.gz.sha256
# macOS
shasum -a 256 -c java-piscine-tester-a0f74962.tar.gz.sha256
```

After the checksum passes, load the image into the engine that will run the tests. For Docker:

```sh
docker load -i java-piscine-tester-a0f74962.tar.gz
docker image inspect zone01athens/java-piscine-tester:a0f74962 --format '{{.Os}}/{{.Architecture}}'
```

Expected output: `linux/amd64`. For Podman, replace `docker` with `podman` in both commands.

## Test a piscine exercise

Use the exact exercise name, filename, package, and Java version specified in the Platform brief. Place the Java files directly under `<Exercise>/` at the repository root. For example, use `HelloWorld/HelloWorld.java`.

Start Docker or Podman with `linux/amd64` support. On Apple Silicon, enable amd64 emulation. Run the tester from the repository root:

```sh
./tools/test-exercise HelloWorld
```

For a different solution directory, pass its path as the second argument. To select Podman explicitly, prefix the command with `CONTAINER_ENGINE=podman`.

**IntelliJ IDEA.** Enable the Shell Script plugin and select **Java Piscine → Run**. The configuration runs `HelloWorld` by default. To switch exercises, set **Run → Edit Configurations → Java Piscine → Script options** to the exercise name.

The runner uses the verified local image and returns the tester’s exit code. If the image is missing, install it from the Zone01 release. Submit each solution as specified in its Platform brief and update your board.

## Push and submit

Use a private GitHub student copy as `origin`. Open the exercise in the Platform and copy its assigned Gitea clone URL and submission branch. Set the variables below to those exact values. Never push the starter to another student's repository.

```sh
git remote add gitea "$GITEA_URL"
git fetch gitea
git remote -v
git add HelloWorld/HelloWorld.java
git commit -m "Complete HelloWorld"
git push origin HEAD
git push gitea "HEAD:refs/heads/$GITEA_BRANCH"
git rev-parse HEAD
git ls-remote gitea "refs/heads/$GITEA_BRANCH"
```

Match the two commit IDs before submitting in the Platform UI. Open the assigned exercise, request evaluation and check its recorded result. If Gitea rejects a non-fast-forward push, inspect its existing history and reconcile it before retrying. Never force-push. If a stage assigns a separate Gitea repository, use a separate checkout with its assigned history and copy only that stage’s required files. Follow the Platform session rules for exams and the team submission and audit rules for raids.

Track each stage on the piscine board after the Platform records its result. A local test or a GitHub card alone cannot award completion.

## License

Use private student repositories. See [Restricted Educational License](LICENSE).

## Cohort calendar

Declare your available hours before kickoff. Staff assign three-person raid teams and publish confirmed dates and times. See the [15-hour weekly schedule](SCHEDULE.md).
