using System.Text.Json.Serialization;

namespace VoltPy.Loader;

public sealed record AppManifest(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("version")] string Version,
    [property: JsonPropertyName("entry")] string Entry,
    [property: JsonPropertyName("dependencies")] IReadOnlyList<string> Dependencies);
