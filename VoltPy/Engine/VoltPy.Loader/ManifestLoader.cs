using System.Text.Json;

namespace VoltPy.Loader;

public sealed class ManifestLoader
{
    private static readonly string[] EntrypointPriority = ["App.py", "main.py", "teste.py"];

    private readonly JsonSerializerOptions _json = new(JsonSerializerDefaults.Web)
    {
        ReadCommentHandling = JsonCommentHandling.Skip,
        AllowTrailingCommas = true,
    };

    public AppManifest LoadOrDiscover(string appDirectory, string? explicitEntry = null)
    {
        var manifestPath = Path.Combine(appDirectory, "manifest.json");
        if (File.Exists(manifestPath))
        {
            var manifest = JsonSerializer.Deserialize<AppManifest>(File.ReadAllText(manifestPath), _json)
                ?? throw new InvalidOperationException($"Manifest inválido: {manifestPath}");

            var entry = ResolveEntry(appDirectory, explicitEntry ?? manifest.Entry);
            var name = string.IsNullOrWhiteSpace(manifest.Name) ? Path.GetFileName(appDirectory) : manifest.Name;
            return manifest with
            {
                Name = name,
                Entry = Path.GetRelativePath(appDirectory, entry),
                Dependencies = manifest.Dependencies ?? Array.Empty<string>(),
            };
        }

        var discovered = ResolveEntry(appDirectory, explicitEntry);
        return new AppManifest(
            Path.GetFileName(appDirectory),
            "0.0.0",
            Path.GetRelativePath(appDirectory, discovered),
            Array.Empty<string>());
    }

    public string ResolveEntry(string appDirectory, string? explicitEntry = null)
    {
        var candidates = new[] { explicitEntry }.Concat(EntrypointPriority).Where(candidate => !string.IsNullOrWhiteSpace(candidate));
        foreach (var candidate in candidates)
        {
            var entry = Path.GetFullPath(Path.Combine(appDirectory, candidate!));
            var relativeEntry = Path.GetRelativePath(appDirectory, entry);
            if (relativeEntry.StartsWith("..", StringComparison.Ordinal) || Path.IsPathRooted(relativeEntry))
            {
                throw new InvalidOperationException("Entry do app VoltPy não pode apontar para fora do diretório do app.");
            }

            if (File.Exists(entry))
            {
                return entry;
            }
        }

        throw new FileNotFoundException($"Nenhum entrypoint VoltPy encontrado em {appDirectory}. Crie App.py, main.py, teste.py ou manifest.json.");
    }
}
