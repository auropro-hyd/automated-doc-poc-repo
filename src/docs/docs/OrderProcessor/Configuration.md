# Configuration

## [BackgroundTaskOptions](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/OrderProcessor/BackgroundTaskOptions.cs#L1-L9)

### Overview
BackgroundTaskOptions is a configuration class that holds settings for background task timing in the OrderProcessor service. It provides two properties: `GracePeriodTime` and `CheckUpdateTime`, which control the grace period duration and the interval for checking updates, respectively. This class is used by services that require configurable timing, such as GracePeriodManagerService, and is typically bound to configuration sources at startup.

### Properties
- **GracePeriodTime** (int): Number of minutes for the grace period. Used to determine when orders are eligible for further processing.
- **CheckUpdateTime** (int): Number of seconds between update checks. Controls the polling interval for background tasks.

### Configuration

| Key                | Default | Effect                                      |
|--------------------|---------|---------------------------------------------|
| GracePeriodTime    | N/A     | Sets the grace period for order processing. |
| CheckUpdateTime    | N/A     | Sets the interval for background checks.    |
