using System.Text.Json;

namespace VoltPy.Loader;

public sealed class ManifestLoader
{
    private readonly JsonSerializerOptions _json = new(JsonSerializerDefaults.Web)
    {
        ReadCommentHandling = JsonCommentHandling.Skip,
        AllowTrailingCommas = true,
    };

    public AppManifest Load(string appDirectory)
    {
        var manifestPath = Path.Combine(appDirectory, "manifest.json");
        if (!File.Exists(manifestPath))
        {
            throw new FileNotFoundException("manifest.json não encontrado para o app VoltPy.", manifestPath);
        }

        var manifest = JsonSerializer.Deserialize<AppManifest>(File.ReadAllText(manifestPath), _json)
            ?? throw new InvalidOperationException($"Manifest inválido: {manifestPath}");

        if (string.IsNullOrWhiteSpace(manifest.Name) || string.IsNullOrWhiteSpace(manifest.Entry))
        {
            throw new InvalidOperationException("Manifest deve declarar name e entry.");
        }

        return manifest with { Dependencies = manifest.Dependencies ?? Array.Empty<string>() };
    }
}
