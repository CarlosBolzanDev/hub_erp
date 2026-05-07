using System.Text.Json.Serialization;

namespace VoltPy.Runtime;

/// <summary>
/// Configuração serializável dos caminhos físicos da instalação VoltPy.
/// Caminhos relativos são resolvidos contra <see cref="VoltPyRoot"/>; o próprio
/// VoltPyRoot relativo é resolvido contra o diretório do arquivo de configuração
/// ou contra o diretório de trabalho do host.
/// </summary>
public sealed record VoltPyPathOptions
{
    [JsonPropertyName("VoltPyRoot")]
    public string? VoltPyRoot { get; init; }

    [JsonPropertyName("NamespaceDirectory")]
    public string? NamespaceDirectory { get; init; }

    [JsonPropertyName("RuntimeDirectory")]
    public string? RuntimeDirectory { get; init; }

    [JsonPropertyName("PackagesDirectory")]
    public string? PackagesDirectory { get; init; }

    [JsonPropertyName("AppsDirectory")]
    public string? AppsDirectory { get; init; }

    [JsonPropertyName("LogsDirectory")]
    public string? LogsDirectory { get; init; }

    [JsonPropertyName("TempDirectory")]
    public string? TempDirectory { get; init; }

    [JsonPropertyName("ConfigDirectory")]
    public string? ConfigDirectory { get; init; }

    [JsonPropertyName("EngineDirectory")]
    public string? EngineDirectory { get; init; }

    [JsonPropertyName("PythonExecutable")]
    public string? PythonExecutable { get; init; }

    [JsonPropertyName("PythonHome")]
    public string? PythonHome { get; init; }

    [JsonPropertyName("UseSystemPythonFallback")]
    public bool? UseSystemPythonFallback { get; init; }

    [JsonPropertyName("AdditionalPythonPath")]
    public IReadOnlyList<string>? AdditionalPythonPath { get; init; }
}
