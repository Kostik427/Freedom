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
	domainSet map[string]struct{}
}

func NewReverseIPLookup() *ReverseIPLookup {
	return &ReverseIPLookup{
		domainSet: make(map[string]struct{}),
	}
}

func (r *ReverseIPLookup) fetchDomainsFromHackerTarget(ip string) ([]string, error) {
	url := fmt.Sprintf("https://api.hackertarget.com/reverseiplookup/?q=%s", ip)
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("HackerTarget API error: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HackerTarget API non-OK status: %d", resp.StatusCode)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading HackerTarget response: %w", err)
	}

	domains := strings.Split(strings.TrimSpace(string(body)), "\n")
	return domains, nil
}

func (r *ReverseIPLookup) fetchDomainsFromSecurityTrails(ip, apiKey string) ([]string, error) {
	url := fmt.Sprintf("https://api.securitytrails.com/v1/ips/%s/domains", ip)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("SecurityTrails request creation error: %w", err)
	}
	req.Header.Add("apikey", apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("SecurityTrails API error: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("SecurityTrails API non-OK status: %d", resp.StatusCode)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading SecurityTrails response: %w", err)
	}

	var data struct {
		Domains []string `json:"domains"`
	}
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, fmt.Errorf("error parsing SecurityTrails JSON: %w", err)
	}

	return data.Domains, nil
}

func (r *ReverseIPLookup) processSingleIP(ip, apiKey string, wg *sync.WaitGroup) {
	defer wg.Done()

	domainSet := make(map[string]struct{})

	hackerTargetDomains, err := r.fetchDomainsFromHackerTarget(ip)
	if err != nil {
		log.Printf("HackerTarget error for IP %s: %v", ip, err)
	} else {
		for _, domain := range hackerTargetDomains {
			domainSet[domain] = struct{}{}
		}
	}

	if apiKey != "" {
		securityTrailsDomains, err := r.fetchDomainsFromSecurityTrails(ip, apiKey)
		if err != nil {
			log.Printf("SecurityTrails error for IP %s: %v", ip, err)
		} else {
			for _, domain := range securityTrailsDomains {
				domainSet[domain] = struct{}{}
			}
		}
	}

	for domain := range domainSet {
		r.domainSet[domain] = struct{}{}
	}
}

func (r *ReverseIPLookup) processAllIPs(ips []string, apiKey string) {
	var wg sync.WaitGroup

	for _, ip := range ips {
		if strings.TrimSpace(ip) == "" {
			continue
		}
		wg.Add(1)
		go r.processSingleIP(ip, apiKey, &wg)
	}

	wg.Wait()
}

func (r *ReverseIPLookup) saveToFile(filename string) {
	file, err := ioutil.TempFile(".", filename)
	if err != nil {
		log.Fatalf("Could not create file: %v", err)
	}
	defer file.Close()

	for domain := range r.domainSet {
		if _, err := file.WriteString(fmt.Sprintf("%s\n", domain)); err != nil {
			log.Fatalf("Could not write to file: %v", err)
		}
	}
	fmt.Printf("Results saved to %s\n", filename)
}

func main() {
	inputFile := "iptables.txt"
	outputFile := "domains_found.txt"
	apiKey := "YOUR_API_KEY"

	data, err := ioutil.ReadFile(inputFile)
	if err != nil {
		log.Fatalf("Error reading input file: %v", err)
	}
	ips := strings.Split(strings.TrimSpace(string(data)), "\n")

	lookup := NewReverseIPLookup()
	lookup.processAllIPs(ips, apiKey)
	lookup.saveToFile(outputFile)
}

