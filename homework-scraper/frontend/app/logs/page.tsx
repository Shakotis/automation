"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import { Tabs, Tab } from "@heroui/tabs";
import { Select, SelectItem } from "@heroui/select";
import { Switch } from "@heroui/switch";
import { Spinner } from "@heroui/spinner";
import { addToast } from "@heroui/toast";
import { title } from "@/components/primitives";
import { monitoringAPI } from "@/lib/api";

interface SystemInfo {
  hostname: string;
  system: string;
  release: string;
  version: string;
  machine: string;
  processor: string;
  timestamp: string;
  uptime?: string;
  memory?: string;
  disk?: string;
  cpu?: string;
}

interface Service {
  name: string;
  status: string;
  details: string;
}

export default function ServerLogsPage() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [logs, setLogs] = useState<string>("");
  const [errors, setErrors] = useState<string>("");
  const [processes, setProcesses] = useState<string>("");
  const [selectedLogType, setSelectedLogType] = useState("django");
  const [logLines, setLogLines] = useState(100);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  const fetchSystemStatus = useCallback(async () => {
    try {
      const data = await monitoringAPI.getSystemStatus();
      if (data.success) {
        setSystemInfo(data.system_info);
      }
    } catch (error) {
      console.error("Error fetching system status:", error);
    }
  }, []);

  const fetchServices = useCallback(async () => {
    try {
      const data = await monitoringAPI.getRunningServices();
      if (data.success) {
        setServices(data.services);
      }
    } catch (error) {
      console.error("Error fetching services:", error);
    }
  }, []);

  const fetchLogs = useCallback(async () => {
    try {
      const data = await monitoringAPI.getApplicationLogs({
        type: selectedLogType as any,
        lines: logLines,
      });
      if (data.success) {
        setLogs(data.logs);
      }
    } catch (error) {
      console.error("Error fetching logs:", error);
      addToast({
        title: "Error",
        description: "Failed to fetch logs. Make sure you're authenticated.",
        color: "danger",
      });
    }
  }, [selectedLogType, logLines]);

  const fetchErrors = useCallback(async () => {
    try {
      const data = await monitoringAPI.getRecentErrors(50);
      if (data.success) {
        setErrors(data.errors);
      }
    } catch (error) {
      console.error("Error fetching errors:", error);
    }
  }, []);

  const fetchProcesses = useCallback(async () => {
    try {
      const data = await monitoringAPI.getProcessInfo();
      if (data.success) {
        setProcesses(data.processes);
      }
    } catch (error) {
      console.error("Error fetching processes:", error);
    }
  }, []);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    await Promise.all([
      fetchSystemStatus(),
      fetchServices(),
      fetchLogs(),
      fetchErrors(),
      fetchProcesses(),
    ]);
    setLoading(false);
  }, [fetchSystemStatus, fetchServices, fetchLogs, fetchErrors, fetchProcesses]);

  useEffect(() => {
    fetchAllData();
  }, []);

  useEffect(() => {
    fetchLogs();
  }, [selectedLogType, logLines]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchAllData();
      }, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, fetchAllData]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "success";
      case "inactive":
      case "failed":
        return "danger";
      case "not-found":
        return "warning";
      default:
        return "default";
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 flex justify-center items-center min-h-[400px]">
        <Spinner size="lg" label="Loading server status..." />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 max-w-7xl">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <h1 className={title({ class: "text-2xl sm:text-3xl", size: "sm" })}>
          Server Monitoring
        </h1>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full sm:w-auto">
          <div className="flex items-center gap-2">
            <Switch
              isSelected={autoRefresh}
              onValueChange={setAutoRefresh}
              size="sm"
            >
              <span className="text-sm">Auto-refresh</span>
            </Switch>
          </div>
          <Button
            size="sm"
            color="primary"
            onPress={fetchAllData}
            className="w-full sm:w-auto"
          >
            🔄 Refresh
          </Button>
        </div>
      </div>

      <Tabs
        selectedKey={activeTab}
        onSelectionChange={(key) => setActiveTab(key as string)}
        className="mb-6"
        classNames={{
          tabList: "overflow-x-auto flex-nowrap",
        }}
      >
        <Tab key="overview" title="Overview">
          <div className="space-y-4 sm:space-y-6">
            {/* System Information */}
            <Card>
              <CardHeader className="p-4">
                <h2 className="text-lg sm:text-xl font-semibold">System Information</h2>
              </CardHeader>
              <CardBody className="p-4 pt-0">
                {systemInfo ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
                    <div>
                      <p className="text-xs sm:text-sm text-default-500">Hostname</p>
                      <p className="font-medium text-sm sm:text-base break-all">{systemInfo.hostname}</p>
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm text-default-500">System</p>
                      <p className="font-medium text-sm sm:text-base">{systemInfo.system} {systemInfo.machine}</p>
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm text-default-500">Release</p>
                      <p className="font-medium text-sm sm:text-base break-all">{systemInfo.release}</p>
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm text-default-500">Uptime</p>
                      <p className="font-medium text-sm sm:text-base">{systemInfo.uptime || "N/A"}</p>
                    </div>
                    {systemInfo.memory && (
                      <div className="md:col-span-2">
                        <p className="text-xs sm:text-sm text-default-500">Memory</p>
                        <p className="font-mono text-xs sm:text-sm break-all">{systemInfo.memory}</p>
                      </div>
                    )}
                    {systemInfo.disk && (
                      <div className="md:col-span-2">
                        <p className="text-xs sm:text-sm text-default-500">Disk Usage</p>
                        <p className="font-mono text-xs sm:text-sm break-all">{systemInfo.disk}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-default-500 text-sm">No system information available</p>
                )}
              </CardBody>
            </Card>

            {/* Services Status */}
            <Card>
              <CardHeader className="p-4">
                <h2 className="text-lg sm:text-xl font-semibold">Services Status</h2>
              </CardHeader>
              <CardBody className="p-4 pt-0">
                <div className="space-y-3">
                  {services.length > 0 ? (
                    services.map((service) => (
                      <div
                        key={service.name}
                        className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-3 bg-default-50 rounded-lg gap-2"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm sm:text-base break-all">{service.name}</p>
                          {service.details && (
                            <p className="text-xs text-default-500 mt-1 font-mono break-all line-clamp-2">
                              {service.details.split("\n")[0]}
                            </p>
                          )}
                        </div>
                        <Chip
                          color={getStatusColor(service.status)}
                          size="sm"
                          variant="flat"
                          className="shrink-0"
                        >
                          {service.status}
                        </Chip>
                      </div>
                    ))
                  ) : (
                    <p className="text-default-500 text-sm">No services information available</p>
                  )}
                </div>
              </CardBody>
            </Card>
          </div>
        </Tab>

        <Tab key="logs" title="Logs">
          <Card>
            <CardHeader className="p-4">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 w-full">
                <h2 className="text-lg sm:text-xl font-semibold">Application Logs</h2>
                <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                  <Select
                    label="Log Type"
                    selectedKeys={[selectedLogType]}
                    onSelectionChange={(keys) => setSelectedLogType(Array.from(keys)[0] as string)}
                    className="w-full sm:w-48"
                    size="sm"
                  >
                    <SelectItem key="django">Django</SelectItem>
                    <SelectItem key="celery">Celery</SelectItem>
                    <SelectItem key="celery-beat">Celery Beat</SelectItem>
                    <SelectItem key="nginx">Nginx Access</SelectItem>
                    <SelectItem key="nginx-error">Nginx Error</SelectItem>
                  </Select>
                  <Select
                    label="Lines"
                    selectedKeys={[logLines.toString()]}
                    onSelectionChange={(keys) => setLogLines(parseInt(Array.from(keys)[0] as string))}
                    className="w-full sm:w-32"
                    size="sm"
                  >
                    <SelectItem key="50">50</SelectItem>
                    <SelectItem key="100">100</SelectItem>
                    <SelectItem key="200">200</SelectItem>
                    <SelectItem key="500">500</SelectItem>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardBody className="p-4 pt-0">
              <div className="bg-black text-green-400 p-3 sm:p-4 rounded-lg font-mono text-xs overflow-x-auto max-h-[600px] overflow-y-auto">
                <pre className="whitespace-pre-wrap break-all">{logs || "No logs available"}</pre>
              </div>
            </CardBody>
          </Card>
        </Tab>

        <Tab key="errors" title="Errors">
          <Card>
            <CardHeader className="p-4">
              <div className="flex justify-between items-center w-full">
                <h2 className="text-lg sm:text-xl font-semibold">Recent Errors</h2>
                <Button size="sm" onPress={fetchErrors}>Refresh</Button>
              </div>
            </CardHeader>
            <CardBody className="p-4 pt-0">
              <div className="bg-black text-red-400 p-3 sm:p-4 rounded-lg font-mono text-xs overflow-x-auto max-h-[600px] overflow-y-auto">
                <pre className="whitespace-pre-wrap break-all">{errors || "No recent errors found"}</pre>
              </div>
            </CardBody>
          </Card>
        </Tab>

        <Tab key="processes" title="Processes">
          <Card>
            <CardHeader className="p-4">
              <div className="flex justify-between items-center w-full">
                <h2 className="text-lg sm:text-xl font-semibold">Running Processes</h2>
                <Button size="sm" onPress={fetchProcesses}>Refresh</Button>
              </div>
            </CardHeader>
            <CardBody className="p-4 pt-0">
              <div className="bg-black text-cyan-400 p-3 sm:p-4 rounded-lg font-mono text-xs overflow-x-auto max-h-[600px] overflow-y-auto">
                <pre className="whitespace-pre-wrap break-all">{processes || "No process information available"}</pre>
              </div>
            </CardBody>
          </Card>
        </Tab>
      </Tabs>

      {/* Info Card */}
      <Card className="bg-primary-50 border-primary-200 mt-6">
        <CardBody className="p-4">
          <div className="flex items-start gap-3">
            <div className="text-primary-600 text-xl shrink-0">ℹ️</div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-primary-800 text-sm sm:text-base">SSH Access</h3>
              <p className="text-primary-700 text-xs sm:text-sm mt-1 break-all">
                To access the server directly: <code className="bg-primary-100 px-2 py-1 rounded">ssh -i ~/.ssh/rpi_3 dovydukas@192.168.0.88</code>
              </p>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
