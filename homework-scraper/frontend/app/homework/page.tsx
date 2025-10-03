"use client";

import { useState, useEffect } from "react";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import { Input } from "@heroui/input";
import { Select, SelectItem } from "@heroui/select";
import { Pagination } from "@heroui/pagination";
import { Spinner } from "@heroui/spinner";
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure } from "@heroui/modal";
import { SearchIcon } from "@/components/icons";
import { title } from "@/components/primitives";

interface HomeworkItem {
  id: number;
  title: string;
  description: string;
  due_date: string | null;
  subject: string;
  site: string;
  url: string;
  synced_to_google_tasks: boolean;
  scraped_at: string;
  google_task_id: string;
  completed: boolean;
  completed_at: string | null;
}

export default function HomeworkPage() {
  const [homework, setHomework] = useState<HomeworkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [siteFilter, setSiteFilter] = useState("all");
  const [syncFilter, setSyncFilter] = useState("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedHomework, setSelectedHomework] = useState<HomeworkItem | null>(null);
  
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Mock data for demo
  const mockHomework: HomeworkItem[] = [
    {
      id: 1,
      title: "Matematikos namų darbai - Algebros uždaviniai",
      description: "Spręsti uždavinius 15-20 iš vadovėlio. Ypatingas dėmesys skirtinas kvadratinėms lygtims.",
      due_date: "2025-10-01T10:00:00Z",
      subject: "Matematika",
      site: "manodienynas",
      url: "https://manodienynas.lt/homework/123",
      synced_to_google_tasks: true,
      scraped_at: new Date().toISOString(),
      google_task_id: "task_123",
      completed: false,
      completed_at: null,
    },
    {
      id: 2,
      title: "Lietuvių kalbos rašinys",
      description: "Parašyti rašinį tema 'Pavasaris mano gyvenime'. Apimtis: 300-400 žodžių.",
      due_date: "2025-10-02T14:00:00Z",
      subject: "Lietuvių kalba",
      site: "eduka",
      url: "https://eduka.lt/homework/456",
      synced_to_google_tasks: false,
      scraped_at: new Date().toISOString(),
      google_task_id: "",
      completed: true,
      completed_at: "2025-10-01T08:00:00Z",
    },
    {
      id: 3,
      title: "Fizikos laboratorinis darbas",
      description: "Atlikti laboratorinius darbus Nr. 5 ir 6. Parengti ataskaitas.",
      due_date: "2025-10-03T12:00:00Z",
      subject: "Fizika",
      site: "manodienynas",
      url: "https://manodienynas.lt/homework/789",
      synced_to_google_tasks: true,
      scraped_at: new Date().toISOString(),
      google_task_id: "task_456",
      completed: false,
      completed_at: null,
    },
    {
      id: 4,
      title: "Istorijos referatas",
      description: "Parašyti referatą apie Lietuvos nepriklausomybės atkūrimą. 5-7 puslapiai.",
      due_date: null,
      subject: "Istorija",
      site: "eduka",
      url: "https://eduka.lt/homework/101",
      synced_to_google_tasks: false,
      scraped_at: new Date().toISOString(),
      google_task_id: "",
      completed: false,
      completed_at: null,
    },
  ];

  useEffect(() => {
    fetchHomework();
  }, [currentPage, siteFilter, syncFilter]);

  const fetchHomework = async () => {
    setLoading(true);
    try {
      // In a real app, this would be an API call
      // const response = await fetch(`/api/scraper/homework/?page=${currentPage}&site=${siteFilter}&synced=${syncFilter}`);
      
      // Mock data with filtering
      let filteredHomework = mockHomework;
      
      if (siteFilter !== "all") {
        filteredHomework = filteredHomework.filter(hw => hw.site === siteFilter);
      }
      
      if (syncFilter !== "all") {
        const isSynced = syncFilter === "synced";
        filteredHomework = filteredHomework.filter(hw => hw.synced_to_google_tasks === isSynced);
      }
      
      if (searchTerm) {
        filteredHomework = filteredHomework.filter(hw => 
          hw.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          hw.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          hw.subject.toLowerCase().includes(searchTerm.toLowerCase())
        );
      }
      
      // Sort homework: incomplete first, completed last
      filteredHomework.sort((a, b) => {
        // First sort by completion status (incomplete first)
        if (a.completed !== b.completed) {
          return a.completed ? 1 : -1;
        }
        // Then sort by due date
        if (a.due_date && b.due_date) {
          return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
        }
        return 0;
      });
      
      setHomework(filteredHomework);
      setTotalPages(Math.ceil(filteredHomework.length / 10));
    } catch (error) {
      console.error('Error fetching homework:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async (homeworkIds?: number[]) => {
    setSyncing(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/scraper/homework/sync-google-tasks/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        credentials: 'include',
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}`);
        
        // Update UI to show items as synced
        if (homeworkIds) {
          setHomework(prev => prev.map(hw => 
            homeworkIds.includes(hw.id) ? { ...hw, synced_to_google_tasks: true } : hw
          ));
        } else {
          setHomework(prev => prev.map(hw => ({ ...hw, synced_to_google_tasks: true })));
        }
      } else {
        const error = await response.json();
        alert(`❌ Sync failed: ${error.error || 'Please make sure you are logged in and have connected your Google account.'}`);
      }
    } catch (error) {
      console.error('Error syncing homework:', error);
      alert(`❌ Sync failed: ${error}`);
    } finally {
      setSyncing(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No due date';
    return new Date(dateString).toLocaleDateString('lt-LT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getSiteColor = (site: string) => {
    return site === 'manodienynas' ? 'primary' : 'secondary';
  };

  const unsyncedHomework = homework.filter(hw => !hw.synced_to_google_tasks);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className={title()}>Homework</h1>
        {unsyncedHomework.length > 0 && (
          <Button
            color="success"
            onPress={() => handleSync()}
            isLoading={syncing}
            disabled={syncing}
          >
            Sync All to Google Tasks ({unsyncedHomework.length})
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Search homework..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && fetchHomework()}
              startContent={<SearchIcon size={18} />}
            />
            
            <Select
              placeholder="All Sites"
              selectedKeys={siteFilter === "all" ? [] : [siteFilter]}
              onSelectionChange={(keys) => setSiteFilter(Array.from(keys)[0] as string || "all")}
            >
              <SelectItem key="all">All Sites</SelectItem>
              <SelectItem key="manodienynas">Manodienynas.lt</SelectItem>
              <SelectItem key="eduka">Eduka.lt</SelectItem>
            </Select>
            
            <Select
              placeholder="Sync Status"
              selectedKeys={syncFilter === "all" ? [] : [syncFilter]}
              onSelectionChange={(keys) => setSyncFilter(Array.from(keys)[0] as string || "all")}
            >
              <SelectItem key="all">All</SelectItem>
              <SelectItem key="synced">Synced</SelectItem>
              <SelectItem key="unsynced">Not Synced</SelectItem>
            </Select>
            
            <Button
              color="primary"
              variant="flat"
              onPress={fetchHomework}
            >
              Apply Filters
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Homework List */}
      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="space-y-4">
          {homework.map((item) => (
            <Card 
              key={item.id}
              className={item.completed ? "opacity-60 bg-default-100" : ""}
            >
              <CardBody>
                <div className="flex justify-between items-start">
                  <div 
                    className="flex-1 cursor-pointer"
                    onClick={() => {setSelectedHomework(item); onOpen();}}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className={`font-semibold text-lg ${item.completed ? 'line-through text-default-400' : ''}`}>
                        {item.title}
                      </h3>
                      <Chip
                        size="sm"
                        color={getSiteColor(item.site)}
                        variant="flat"
                      >
                        {item.site}
                      </Chip>
                      {item.completed ? (
                        <Chip size="sm" color="default" variant="flat">
                          ✓ Completed
                        </Chip>
                      ) : (
                        <>
                          {item.synced_to_google_tasks ? (
                            <Chip size="sm" color="success" variant="flat">
                              ✓ Synced
                            </Chip>
                          ) : (
                            <Chip size="sm" color="warning" variant="flat">
                              Not Synced
                            </Chip>
                          )}
                        </>
                      )}
                    </div>
                    
                    <p className={`text-default-600 mb-3 line-clamp-2 ${item.completed ? 'text-default-400' : ''}`}>
                      {item.description}
                    </p>
                    
                    <div className="flex items-center gap-6 text-sm text-default-500">
                      <span>📚 {item.subject}</span>
                      <span>📅 {formatDate(item.due_date)}</span>
                      {item.completed && item.completed_at && (
                        <span>✓ Completed {formatDate(item.completed_at)}</span>
                      )}
                      {!item.completed && (
                        <span>🕒 Scraped {formatDate(item.scraped_at)}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex gap-2 ml-4">
                    {!item.synced_to_google_tasks && (
                      <Button
                        size="sm"
                        color="success"
                        variant="flat"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSync([item.id]);
                        }}
                        isLoading={syncing}
                      >
                        Sync
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="light"
                      as="a"
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                    >
                      View Source
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>
          ))}
          
          {homework.length === 0 && (
            <Card>
              <CardBody className="text-center py-12">
                <p className="text-default-500">No homework found matching your criteria.</p>
              </CardBody>
            </Card>
          )}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center mt-8">
          <Pagination
            total={totalPages}
            page={currentPage}
            onChange={setCurrentPage}
          />
        </div>
      )}

      {/* Homework Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="2xl">
        <ModalContent>
          <ModalHeader className="flex flex-col gap-1">
            {selectedHomework?.title}
          </ModalHeader>
          <ModalBody>
            {selectedHomework && (
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Chip
                    color={getSiteColor(selectedHomework.site)}
                    variant="flat"
                  >
                    {selectedHomework.site}
                  </Chip>
                  {selectedHomework.synced_to_google_tasks ? (
                    <Chip color="success" variant="flat">
                      ✓ Synced to Google Tasks
                    </Chip>
                  ) : (
                    <Chip color="warning" variant="flat">
                      Not Synced
                    </Chip>
                  )}
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Description</h4>
                  <p className="text-default-600">{selectedHomework.description}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold mb-1">Subject</h4>
                    <p className="text-default-600">{selectedHomework.subject}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">Due Date</h4>
                    <p className="text-default-600">{formatDate(selectedHomework.due_date)}</p>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-1">Source URL</h4>
                  <Button
                    as="a"
                    href={selectedHomework.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    variant="light"
                    size="sm"
                  >
                    Open in {selectedHomework.site}
                  </Button>
                </div>
              </div>
            )}
          </ModalBody>
          <ModalFooter>
            <Button color="danger" variant="light" onPress={onClose}>
              Close
            </Button>
            {selectedHomework && !selectedHomework.synced_to_google_tasks && (
              <Button
                color="success"
                onPress={() => {
                  handleSync([selectedHomework.id]);
                  onClose();
                }}
                isLoading={syncing}
              >
                Sync to Google Tasks
              </Button>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
}