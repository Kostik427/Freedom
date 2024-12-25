package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
	"sync"
)

type ReverseIPLookup struct {
	uniqueDomains map[string]struct{}
}

func NewReverseIPLookup() *ReverseIPLookup {
	return &ReverseIPLookup{
		uniqueDomains: make(map[string]struct{}),
	}
}

func (r *ReverseIPLookup) getDomainsHackerTarget(ip string) ([]string, error) {
	url := fmt.Sprintf("https://api.hackertarget.com/reverseiplookup/?q=%s", ip)
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("error with HackerTarget API: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("non-OK status code: %d", resp.StatusCode)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	domains := strings.Split(string(body), "\n")
	var result []string
	for _, domain := range domains {
		domain = strings.TrimSpace(domain)
		if domain != "" {
			result = append(result, domain)
		}
	}
	return result, nil
}

func (r *ReverseIPLookup) getDomainsSecurityTrails(ip, apiKey string) ([]string, error) {
	url := fmt.Sprintf("https://api.securitytrails.com/v1/ips/%s/domains", ip)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("error creating request: %w", err)
	}
	req.Header.Add("apikey", apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error with SecurityTrails API: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("non-OK status code: %d", resp.StatusCode)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}

	// Parse the response body assuming JSON format
	var data struct {
		Domains []string `json:"domains"`
	}
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, fmt.Errorf("error unmarshalling JSON response: %w", err)
	}

	return data.Domains, nil
}

func (r *ReverseIPLookup) processIP(ip, apiKey string, wg *sync.WaitGroup) {
	defer wg.Done()
	fmt.Printf("Processing IP: %s\n", ip)
	domains := make(map[string]struct{})

	// Get domains from HackerTarget
	htDomains, err := r.getDomainsHackerTarget(ip)
	if err != nil {
		log.Println("Error getting HackerTarget domains:", err)
	} else {
		for _, domain := range htDomains {
			domains[domain] = struct{}{}
		}
	}

	// If API key is provided, use SecurityTrails API as well
	if apiKey != "" {
		stDomains, err := r.getDomainsSecurityTrails(ip, apiKey)
		if err != nil {
			log.Println("Error getting SecurityTrails domains:", err)
		} else {
			for _, domain := range stDomains {
				domains[domain] = struct{}{}
			}
		}
	}

	// Update unique domains
	for domain := range domains {
		r.uniqueDomains[domain] = struct{}{}
	}
}

func (r *ReverseIPLookup) processIPs(ips []string, apiKey string) {
	var wg sync.WaitGroup

	for _, ip := range ips {
		wg.Add(1)
		go r.processIP(ip, apiKey, &wg)
	}

	wg.Wait()
}

func (r *ReverseIPLookup) saveResults(outputFile string) {
	file, err := ioutil.TempFile(".", outputFile)
	if err != nil {
		log.Fatalf("Failed to create output file: %v", err)
	}
	defer file.Close()

	for domain := range r.uniqueDomains {
		_, err := file.WriteString(fmt.Sprintf("%s\n", domain))
		if err != nil {
			log.Fatalf("Failed to write to file: %v", err)
		}
	}
	fmt.Printf("Results saved to %s\n", outputFile)
}

func main() {
	inputFile := "iptables.txt"
	outputFile := "domains_found.txt"
	securityTrailsAPIKey := "YOUR_API_KEY"

	// Read IPs from input file
	data, err := ioutil.ReadFile(inputFile)
	if err != nil {
		log.Fatalf("Error reading input file: %v", err)
	}
	ips := strings.Split(string(data), "\n")

	// Initialize reverse IP lookup
	lookup := NewReverseIPLookup()

	// Process IPs concurrently
	lookup.processIPs(ips, securityTrailsAPIKey)

	// Save results to file
	lookup.saveResults(outputFile)
}
